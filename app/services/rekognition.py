import boto3
from typing import Dict, Any
from app.core.config import AWS_DEFAULT_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET

class RekognitionService:
    def __init__(self):
        self.client = boto3.client(
            'rekognition',
            region_name=AWS_DEFAULT_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.bucket = S3_BUCKET

    def analyze_car_image(self, image_key: str) -> Dict[str, Any]:
        try:
            # Detect labels
            label_response = self.client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': self.bucket,
                        'Name': image_key
                    }
                },
                MaxLabels=50,  # Increased for better detection
                MinConfidence=50  # Lowered threshold for better sensitivity
            )

            # Enhanced categories for detection
            car_labels = ['Car', 'Automobile', 'Vehicle', 'Transportation']
            damage_labels = [
                'Damage', 'Dent', 'Scratch', 'Broken', 'Accident', 'Collision',
                'Crashed', 'Wreck', 'Damaged', 'Bent', 'Crushed', 'Crumpled',
                'Smashed', 'Deformed', 'Destroyed'
            ]

            # Process results
            found_labels = label_response['Labels']
            
            # Check for car presence
            is_car = any(
                label['Name'].lower() in [car.lower() for car in car_labels]
                for label in found_labels
            )

            # Enhanced damage detection
            damages = []
            for label in found_labels:
                label_name = label['Name'].lower()
                
                # Check for direct damage labels
                if any(damage.lower() in label_name for damage in damage_labels):
                    damages.append({
                        'name': label['Name'],
                        'confidence': label['Confidence'],
                        'instances': label.get('Instances', [])
                    })
                
                # Check for parent-child relationships that might indicate damage
                for parent in label.get('Parents', []):
                    if parent['Name'].lower() in [d.lower() for d in damage_labels]:
                        damages.append({
                            'name': f"{label['Name']} ({parent['Name']})",
                            'confidence': label['Confidence'],
                            'instances': label.get('Instances', [])
                        })

            # Additional analysis using detect_moderation_labels for severe damage
            moderation_response = self.client.detect_moderation_labels(
                Image={
                    'S3Object': {
                        'Bucket': self.bucket,
                        'Name': image_key
                    }
                },
                MinConfidence=50
            )

            # Check for violence/graphic content which might indicate severe accidents
            accident_indicators = any(
                label['Name'].lower() in ['violence', 'graphic content']
                for label in moderation_response.get('ModerationLabels', [])
            )

            # Determine if damage is detected based on multiple factors
            damage_detected = len(damages) > 0 or accident_indicators

            # Get text in image (might help detect warning signs or damage reports)
            text_response = self.client.detect_text(
                Image={
                    'S3Object': {
                        'Bucket': self.bucket,
                        'Name': image_key
                    }
                }
            )

            damage_related_text = [
                text['DetectedText']
                for text in text_response.get('TextDetections', [])
                if any(damage.lower() in text['DetectedText'].lower() for damage in damage_labels)
            ]

            return {
                "is_vehicle": is_car,
                "damage_detected": damage_detected,
                "confidence_score": max([d['confidence'] for d in damages], default=0) if damages else 0,
                "damage_details": damages,
                "damage_related_text": damage_related_text,
                "all_labels": [
                    {
                        'name': label['Name'],
                        'confidence': label['Confidence'],
                        'parents': [parent['Name'] for parent in label.get('Parents', [])]
                    }
                    for label in found_labels
                ]
            }

        except Exception as e:
            raise Exception(f"Failed to analyze image: {str(e)}")

    def detect_text_in_image(self, image_key: str) -> Dict[str, Any]:
        try:
            # Detect text in the image
            response = self.client.detect_text(
                Image={
                    'S3Object': {
                        'Bucket': self.bucket,
                        'Name': image_key
                    }
                }
            )

            return {
                "detected_text": [
                    {
                        'text': text['DetectedText'],
                        'confidence': text['Confidence'],
                        'type': text['Type']
                    }
                    for text in response['TextDetections']
                ]
            }

        except Exception as e:
            raise Exception(f"Failed to detect text: {str(e)}")