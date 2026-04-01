import sys
import os
import json

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.hybrid_detector import HybridDetector
from app.services.ml_detector import MLDetector

# Initialize the model
MLDetector.load_model()

# Expanded Evaluation Dataset (40 samples)
eval_data = [
    # --- POSITIVES (Dark Patterns) ---
    {"text": "Only 3 items left in stock! Hurry up!", "label": "pattern", "category": "urgency"},
    {"text": "Hurry, limited time offer. Sale ends in 5 minutes.", "label": "pattern", "category": "urgency"},
    {"text": "12 other people have this in their cart right now.", "label": "pattern", "category": "scarcity"},
    {"text": "No thanks, I'd rather pay full price.", "label": "pattern", "category": "confirmshaming"},
    {"text": "A processing fee of $15 will be added at checkout.", "label": "pattern", "category": "hidden_cost"},
    {"text": "Act now! Don't miss out on this deal.", "label": "pattern", "category": "urgency"},
    {"text": "Limited edition item - only few left.", "label": "pattern", "category": "scarcity"},
    {"text": "Get 50% discount if you buy in the next 10 minutes!", "label": "pattern", "category": "urgency"},
    {"text": "Only 2 rooms left on our site!", "label": "pattern", "category": "scarcity"},
    {"text": "Price increases in 02:45. Buy before it's too late.", "label": "pattern", "category": "urgency"},
    {"text": "Join our newsletter to unlock this content for free.", "label": "pattern", "category": "forced-action"},
    {"text": "Shipping fee of $9.99 will be applied to your order.", "label": "pattern", "category": "hidden_cost"},
    {"text": "No, I am not interested in saving money today.", "label": "pattern", "category": "confirmshaming"},
    {"text": "Wait! Others are looking at this same product.", "label": "pattern", "category": "scarcity"},
    {"text": "One-time offer expires soon. Act fast!", "label": "pattern", "category": "urgency"},
    {"text": "Last chance to grab the deal at this price.", "label": "pattern", "category": "urgency"},
    {"text": "Additional service charges and taxes added later.", "label": "pattern", "category": "hidden_cost"},
    {"text": "People in London just bought this product.", "label": "pattern", "category": "scarcity"},
    {"text": "Don't let this items slip away!", "label": "pattern", "category": "pressure"},
    {"text": "This item is in high demand! Hurry!", "label": "pattern", "category": "scarcity"},
    
    # --- SUBTLE/BORDERLINE POSITIVES (Likely False Negatives) ---
    {"text": "Price might change based on availability.", "label": "pattern", "category": "hidden_cost"},
    {"text": "100k customers trust us.", "label": "pattern", "category": "scarcity"},
    {"text": "Subscription renewals are automatic.", "label": "pattern", "category": "sneaking"},
    {"text": "Recommended for most users.", "label": "pattern", "category": "misdirection"},
    {"text": "By continuing, you accept our marketing emails.", "label": "pattern", "category": "forced-action"},
    
    # --- NEGATIVES (Safe UI) ---
    {"text": "Login to your account", "label": "safe", "category": "none"},
    {"text": "Search for products and brands", "label": "safe", "category": "none"},
    {"text": "New chat with Assistant", "label": "safe", "category": "none"},
    {"text": "Privacy policy and terms of use", "label": "safe", "category": "none"},
    {"text": "Copyright 2024. All rights reserved.", "label": "safe", "category": "none"},
    {"text": "Contact our support team for help.", "label": "safe", "category": "none"},
    {"text": "Terms and conditions apply.", "label": "safe", "category": "none"},
    {"text": "View our help center.", "label": "safe", "category": "none"},
    {"text": "Reset your password via email.", "label": "safe", "category": "none"},
    {"text": "Manage your cookie preferences.", "label": "safe", "category": "none"},
    {"text": "Join the global community of learners.", "label": "safe", "category": "none"},
    {"text": "Free shipping on orders over $50.", "label": "safe", "category": "none"},
    {"text": "Official website of the organization.", "label": "safe", "category": "none"},
    
    # --- AMBIGUOUS NEGATIVES (Likely False Positives) ---
    {"text": "Your login session will expire in 5 minutes for safety.", "label": "safe", "category": "none"},
    {"text": "Only 3 spots left for the free webinar registration.", "label": "safe", "category": "none"}
]

results = []

for item in eval_data:
    # We pass empty HTML as we are testing text-based detectionmainly here
    detections = HybridDetector.analyze_and_merge("", item["text"])
    
    is_pattern = len(detections) > 0
    confidence = detections[0].get("confidence", 1.0) if is_pattern else 0.0
    pred_cat = detections[0].get("category", "none") if is_pattern else "none"
    
    results.append({
        "text": item["text"],
        "actual": item["label"],
        "actual_cat": item["category"],
        "pred": "pattern" if is_pattern else "safe",
        "pred_cat": pred_cat,
        "confidence": confidence
    })

# Compute metrics
tp = sum(1 for r in results if r["actual"] == "pattern" and r["pred"] == "pattern")
tn = sum(1 for r in results if r["actual"] == "safe" and r["pred"] == "safe")
fp = sum(1 for r in results if r["actual"] == "safe" and r["pred"] == "pattern")
fn = sum(1 for r in results if r["actual"] == "pattern" and r["pred"] == "safe")

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
accuracy = (tp + tn) / len(results)

print("\n--- RESULTS ---")
print(f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")
print(f"Accuracy: {accuracy:.3f}")

print("\n--- FALSE NEGATIVES ---")
for r in results:
    if r["actual"] == "pattern" and r["pred"] == "safe":
        print(f"- {r['text']} (Expected: {r['actual_cat']})")

print("\n--- FALSE POSITIVES ---")
for r in results:
    if r["actual"] == "safe" and r["pred"] == "pattern":
        print(f"- {r['text']} (Pred: {r['pred_cat']})")
