"""
ReturnIQ Safety Guardrails - 4 Critical Safeguards
1. No Harmful Output
2. PII Protection
3. Factuality Guarantee
4. Fairness & Bias
"""

import re
import logging
from typing import Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SafetyGuardrails:
    """Implements 4 critical safety guardrails"""

    def __init__(self):
        self.pii_patterns = {
            'customer_name': r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        }

        self.harmful_phrases = [
            'delete customer',
            'ban permanently',
            'discriminate against',
            'eliminate from system',
            'harm customer',
            'malicious',
            'harm business',
        ]

        self.pii_audit_log = []

    # =========================================================================
    # GUARDRAIL 1: NO HARMFUL OUTPUT
    # =========================================================================

    def validate_no_harmful_output(self, text: str, confidence: float = None) -> Dict:
        """
        Check for harmful content in recommendations.
        Confidence threshold: <70% = human review mandatory
        """
        try:
            harmful_detected = False
            harmful_items = []

            # Check for harmful phrases
            for phrase in self.harmful_phrases:
                if phrase.lower() in text.lower():
                    harmful_detected = True
                    harmful_items.append(f"Detected harmful phrase: '{phrase}'")

            # Check confidence threshold
            if confidence and confidence < 0.70:
                harmful_detected = True
                harmful_items.append(f"Confidence below threshold ({confidence:.1%} < 70%)")

            return {
                "status": "flagged" if harmful_detected else "approved",
                "harmful_detected": harmful_detected,
                "items": harmful_items,
                "action": "flag_for_human_review" if harmful_detected else "proceed"
            }

        except Exception as e:
            logger.error(f"Harmful content check error: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =========================================================================
    # GUARDRAIL 2: PII PROTECTION
    # =========================================================================

    def mask_pii(self, text: str) -> str:
        """
        Automatically mask PII in logs and outputs
        """
        try:
            masked_text = text

            # Mask customer names
            masked_text = re.sub(self.pii_patterns['customer_name'], '[CUSTOMER_NAME]', masked_text)

            # Mask emails
            masked_text = re.sub(self.pii_patterns['email'], '[EMAIL]', masked_text)

            # Mask phone numbers
            masked_text = re.sub(self.pii_patterns['phone'], '[PHONE]', masked_text)

            # Mask SSN
            masked_text = re.sub(self.pii_patterns['ssn'], '[SSN]', masked_text)

            # Mask credit cards
            masked_text = re.sub(self.pii_patterns['credit_card'], '[CREDIT_CARD]', masked_text)

            return masked_text

        except Exception as e:
            logger.error(f"PII masking error: {str(e)}")
            return text

    def log_pii_access(self, user_id: str, action: str, resource_id: str, pii_fields: List[str]):
        """
        Audit trail: log all PII access for compliance
        """
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "action": action,
                "resource_id": resource_id,
                "pii_fields_accessed": pii_fields,
                "status": "logged"
            }

            self.pii_audit_log.append(audit_entry)
            logger.info(f"PII access logged: {json.dumps(audit_entry)}")

            return audit_entry

        except Exception as e:
            logger.error(f"PII audit log error: {str(e)}")

    def validate_pii_protection(self, recommendation: Dict) -> Dict:
        """
        Validate that PII is properly protected in recommendations
        """
        try:
            issues = []

            # Check for exposed customer names
            if 'customer_name' in recommendation and recommendation['customer_name']:
                if not recommendation['customer_name'].startswith('['):
                    issues.append("Customer name not masked")

            # Check for exposed emails
            if re.search(self.pii_patterns['email'], json.dumps(recommendation)):
                issues.append("Email address exposed in recommendation")

            # Check for exposed phone numbers
            if re.search(self.pii_patterns['phone'], json.dumps(recommendation)):
                issues.append("Phone number exposed in recommendation")

            return {
                "status": "flagged" if issues else "approved",
                "pii_issues": issues,
                "action": "flag_for_human_review" if issues else "proceed"
            }

        except Exception as e:
            logger.error(f"PII validation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =========================================================================
    # GUARDRAIL 3: FACTUALITY GUARANTEE
    # =========================================================================

    def validate_factuality(self, recommendation: Dict) -> Dict:
        """
        Ensure every recommendation includes evidence.
        Hallucination detection: if evidence missing, flag for human review.
        """
        try:
            issues = []

            # Check for evidence
            if not recommendation.get('evidence'):
                issues.append("No evidence provided")

            if not recommendation.get('evidence_returns'):
                issues.append("No supporting return IDs cited")

            # Check that all cited returns actually exist
            if recommendation.get('evidence_returns'):
                # In production: query database to verify
                for return_id in recommendation['evidence_returns']:
                    if not self._verify_return_exists(return_id):
                        issues.append(f"Invalid evidence reference: {return_id}")

            # Check for statistical claims without backing
            if 'statistical_claim' in recommendation:
                if not recommendation.get('statistical_support'):
                    issues.append("Statistical claim without supporting data")

            # Check for confidence score
            if not recommendation.get('confidence'):
                issues.append("No confidence score provided")
            elif recommendation['confidence'] < 0.70:
                issues.append(f"Low confidence ({recommendation['confidence']:.1%})")

            return {
                "status": "flagged" if issues else "approved",
                "hallucination_risk": len(issues) > 0,
                "factuality_issues": issues,
                "action": "flag_for_human_review" if issues else "proceed"
            }

        except Exception as e:
            logger.error(f"Factuality validation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _verify_return_exists(self, return_id: str) -> bool:
        """Verify return exists in database (mock implementation)"""
        # In production: query PostgreSQL
        return True  # Mock: assume all returns exist

    def detect_hallucinations(self, response_text: str, source_data: Dict) -> Dict:
        """
        Detect if Claude is hallucinating (making up data)
        """
        try:
            hallucinations = []
            confidence = 0.95

            # Check if claimed statistics exist in source data
            if 'statistics' in response_text:
                # Parse statistics from response
                stats = self._extract_statistics(response_text)

                for stat in stats:
                    if not self._verify_statistic(stat, source_data):
                        hallucinations.append(f"Unverified statistic: {stat}")
                        confidence -= 0.1

            # Check if claimed examples exist
            if 'example' in response_text.lower():
                examples = self._extract_examples(response_text)

                for example in examples:
                    if not self._verify_example(example, source_data):
                        hallucinations.append(f"Unverified example: {example}")
                        confidence -= 0.1

            return {
                "hallucinations_detected": len(hallucinations) > 0,
                "hallucination_count": len(hallucinations),
                "hallucination_items": hallucinations,
                "confidence": max(0, confidence),
                "action": "flag" if len(hallucinations) > 0 else "approve"
            }

        except Exception as e:
            logger.error(f"Hallucination detection error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _extract_statistics(self, text: str) -> List[str]:
        """Extract statistical claims from text"""
        # Simple regex for percentage claims
        return re.findall(r'\d+%', text)

    def _extract_examples(self, text: str) -> List[str]:
        """Extract example claims from text"""
        return []  # Mock implementation

    def _verify_statistic(self, stat: str, source_data: Dict) -> bool:
        """Verify if statistic is in source data"""
        return True  # Mock: assume statistic is valid

    def _verify_example(self, example: str, source_data: Dict) -> bool:
        """Verify if example exists in source data"""
        return True  # Mock: assume example is valid

    # =========================================================================
    # GUARDRAIL 4: FAIRNESS & BIAS
    # =========================================================================

    def validate_fairness(self, recommendation: Dict, demographic_data: Dict) -> Dict:
        """
        Check for demographic parity and bias.
        Flag if recommendation disproportionately impacts one demographic.
        """
        try:
            bias_issues = []
            demographic_impact = {}

            # Check demographic parity
            demographics = ['age_group', 'gender', 'location', 'customer_segment']

            for demo in demographics:
                if demo in demographic_data:
                    # Calculate accuracy by demographic
                    accuracy = self._calculate_accuracy_by_demographic(demo, demographic_data)
                    demographic_impact[demo] = accuracy

                    # Flag if any segment has <70% accuracy
                    for segment, segment_accuracy in accuracy.items():
                        if segment_accuracy < 0.70:
                            bias_issues.append(f"Demographic disparity: {demo}={segment} has {segment_accuracy:.1%} accuracy")

            # Check impact distribution
            impact_by_demo = self._measure_impact_distribution(recommendation, demographic_data)

            for demo, distribution in impact_by_demo.items():
                if max(distribution) > 0 and min(distribution) > 0:
                    disparity_ratio = max(distribution) / min(distribution)

                    if disparity_ratio > 1.3:  # >30% disparity
                        bias_issues.append(f"Disproportionate impact on {demo}: {disparity_ratio:.1f}x difference")

            return {
                "status": "flagged" if bias_issues else "approved",
                "fairness_score": 1.0 - (len(bias_issues) * 0.1),
                "bias_issues": bias_issues,
                "demographic_impact": demographic_impact,
                "action": "flag_for_human_review" if bias_issues else "proceed"
            }

        except Exception as e:
            logger.error(f"Fairness validation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _calculate_accuracy_by_demographic(self, demographic: str, demographic_data: Dict) -> Dict:
        """Calculate accuracy for each demographic segment"""
        # Mock implementation
        return {
            'segment_1': 0.85,
            'segment_2': 0.92,
            'segment_3': 0.78
        }

    def _measure_impact_distribution(self, recommendation: Dict, demographic_data: Dict) -> Dict:
        """Measure how recommendation impacts different demographics"""
        # Mock implementation
        return {
            'age_group': [100, 120, 95],
            'gender': [110, 105],
            'location': [98, 115, 92]
        }

    # =========================================================================
    # COMBINED VALIDATION
    # =========================================================================

    def validate_recommendation(self, recommendation: Dict) -> Dict:
        """
        Comprehensive validation: all 4 guardrails
        """
        try:
            validations = {
                "harmful_output": self.validate_no_harmful_output(
                    recommendation.get('text', ''),
                    recommendation.get('confidence')
                ),
                "pii_protection": self.validate_pii_protection(recommendation),
                "factuality": self.validate_factuality(recommendation),
                "fairness": self.validate_fairness(recommendation, {})
            }

            # Overall status
            all_approved = all(v.get('status') == 'approved' for v in validations.values())

            return {
                "status": "approved" if all_approved else "flagged",
                "validations": validations,
                "overall_confidence": self._calculate_overall_confidence(validations),
                "recommendation": "proceed" if all_approved else "human_review"
            }

        except Exception as e:
            logger.error(f"Combined validation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def validate_confidence_threshold(self, confidence: float) -> bool:
        """Check if confidence meets threshold for auto-approval"""
        return confidence >= 0.70

    def _calculate_overall_confidence(self, validations: Dict) -> float:
        """Calculate overall confidence score across all validations"""
        scores = []

        for validation in validations.values():
            if 'confidence' in validation:
                scores.append(validation['confidence'])
            elif validation.get('status') == 'approved':
                scores.append(1.0)
            else:
                scores.append(0.5)

        return sum(scores) / len(scores) if scores else 0.0
