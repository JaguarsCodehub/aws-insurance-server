import boto3
from app.core.config import AWS_DEFAULT_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def create_damage_analysis_table():
    dynamodb = boto3.client(
        'dynamodb',
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    try:
        # Create the table
        response = dynamodb.create_table(
            TableName='car_damage_analyses',
            KeySchema=[
                {
                    'AttributeName': 'analysis_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'analysis_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'damage_detected',
                    'AttributeType': 'N'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'damage_detected-timestamp-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'damage_detected',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table created successfully!")
        return response
    except dynamodb.exceptions.ResourceInUseException:
        print("Table already exists!")
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        raise e

if __name__ == "__main__":
    create_damage_analysis_table()