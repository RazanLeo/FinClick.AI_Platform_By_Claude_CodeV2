// MongoDB Initialization Script for FinClick.AI Platform
// This script creates the database, collections, and initial data

// Switch to the FinClick.AI database
db = db.getSiblingDB('finclick_ai');

// Create application user
db.createUser({
  user: 'finclick_app',
  pwd: 'FinClick2024SecurePassword!',
  roles: [
    {
      role: 'readWrite',
      db: 'finclick_ai'
    }
  ]
});

// Create collections with validation schemas

// 1. Document Storage Collection
db.createCollection('documents', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['userId', 'fileName', 'fileType', 'uploadedAt'],
      properties: {
        userId: {
          bsonType: 'string',
          description: 'User ID who uploaded the document'
        },
        fileName: {
          bsonType: 'string',
          description: 'Original filename'
        },
        fileType: {
          bsonType: 'string',
          enum: ['pdf', 'image', 'excel', 'csv', 'txt'],
          description: 'Type of document'
        },
        fileSize: {
          bsonType: 'number',
          minimum: 0,
          description: 'File size in bytes'
        },
        mimeType: {
          bsonType: 'string',
          description: 'MIME type of the file'
        },
        storagePath: {
          bsonType: 'string',
          description: 'Path where file is stored'
        },
        metadata: {
          bsonType: 'object',
          description: 'Additional file metadata'
        },
        tags: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'Document tags'
        },
        category: {
          bsonType: 'string',
          enum: ['statement', 'receipt', 'invoice', 'contract', 'report', 'other'],
          description: 'Document category'
        },
        isEncrypted: {
          bsonType: 'bool',
          description: 'Whether the document is encrypted'
        },
        uploadedAt: {
          bsonType: 'date',
          description: 'Upload timestamp'
        },
        lastAccessedAt: {
          bsonType: 'date',
          description: 'Last access timestamp'
        },
        expiresAt: {
          bsonType: 'date',
          description: 'Document expiration date'
        }
      }
    }
  }
});

// 2. Analysis Results Collection
db.createCollection('analysis_results', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['userId', 'analysisType', 'result', 'createdAt'],
      properties: {
        userId: {
          bsonType: 'string',
          description: 'User ID'
        },
        analysisType: {
          bsonType: 'string',
          enum: ['spending_analysis', 'budget_forecast', 'investment_analysis', 'risk_assessment', 'pattern_detection', 'anomaly_detection'],
          description: 'Type of analysis performed'
        },
        inputData: {
          bsonType: 'object',
          description: 'Input data used for analysis'
        },
        result: {
          bsonType: 'object',
          description: 'Analysis results'
        },
        confidence: {
          bsonType: 'number',
          minimum: 0,
          maximum: 1,
          description: 'Confidence score of the analysis'
        },
        metadata: {
          bsonType: 'object',
          description: 'Analysis metadata and parameters'
        },
        processingTime: {
          bsonType: 'number',
          minimum: 0,
          description: 'Processing time in milliseconds'
        },
        version: {
          bsonType: 'string',
          description: 'Analysis algorithm version'
        },
        tags: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'Analysis tags'
        },
        createdAt: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        expiresAt: {
          bsonType: 'date',
          description: 'Result expiration date'
        }
      }
    }
  }
});

// 3. User Activity Logs Collection
db.createCollection('user_activity_logs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['userId', 'action', 'timestamp'],
      properties: {
        userId: {
          bsonType: 'string',
          description: 'User ID'
        },
        sessionId: {
          bsonType: 'string',
          description: 'User session ID'
        },
        action: {
          bsonType: 'string',
          description: 'Action performed by user'
        },
        resource: {
          bsonType: 'string',
          description: 'Resource accessed or modified'
        },
        resourceId: {
          bsonType: 'string',
          description: 'ID of the resource'
        },
        details: {
          bsonType: 'object',
          description: 'Additional action details'
        },
        ipAddress: {
          bsonType: 'string',
          description: 'User IP address'
        },
        userAgent: {
          bsonType: 'string',
          description: 'User agent string'
        },
        location: {
          bsonType: 'object',
          properties: {
            country: { bsonType: 'string' },
            city: { bsonType: 'string' },
            coordinates: {
              bsonType: 'array',
              items: { bsonType: 'number' }
            }
          },
          description: 'User location data'
        },
        deviceInfo: {
          bsonType: 'object',
          description: 'Device information'
        },
        timestamp: {
          bsonType: 'date',
          description: 'Action timestamp'
        }
      }
    }
  }
});

// 4. File Processing Queue Collection
db.createCollection('file_processing_queue', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['documentId', 'processingType', 'status', 'createdAt'],
      properties: {
        documentId: {
          bsonType: 'string',
          description: 'Reference to document'
        },
        processingType: {
          bsonType: 'string',
          enum: ['ocr', 'classification', 'data_extraction', 'analysis', 'virus_scan'],
          description: 'Type of processing to perform'
        },
        status: {
          bsonType: 'string',
          enum: ['pending', 'processing', 'completed', 'failed', 'cancelled'],
          description: 'Processing status'
        },
        priority: {
          bsonType: 'number',
          minimum: 1,
          maximum: 10,
          description: 'Processing priority (1=highest, 10=lowest)'
        },
        attempts: {
          bsonType: 'number',
          minimum: 0,
          description: 'Number of processing attempts'
        },
        maxAttempts: {
          bsonType: 'number',
          minimum: 1,
          description: 'Maximum number of attempts'
        },
        processingParams: {
          bsonType: 'object',
          description: 'Processing parameters'
        },
        result: {
          bsonType: 'object',
          description: 'Processing result'
        },
        error: {
          bsonType: 'object',
          description: 'Error information if processing failed'
        },
        startedAt: {
          bsonType: 'date',
          description: 'Processing start time'
        },
        completedAt: {
          bsonType: 'date',
          description: 'Processing completion time'
        },
        createdAt: {
          bsonType: 'date',
          description: 'Queue entry creation time'
        }
      }
    }
  }
});

// 5. ML Model Training Data Collection
db.createCollection('ml_training_data', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['modelType', 'features', 'labels', 'createdAt'],
      properties: {
        modelType: {
          bsonType: 'string',
          enum: ['spending_prediction', 'anomaly_detection', 'categorization', 'risk_assessment'],
          description: 'Type of ML model'
        },
        features: {
          bsonType: 'object',
          description: 'Feature vector for training'
        },
        labels: {
          bsonType: 'object',
          description: 'Labels for supervised learning'
        },
        userId: {
          bsonType: 'string',
          description: 'User ID (for personalized models)'
        },
        dataSource: {
          bsonType: 'string',
          description: 'Source of training data'
        },
        version: {
          bsonType: 'string',
          description: 'Data version'
        },
        isValidated: {
          bsonType: 'bool',
          description: 'Whether data has been validated'
        },
        metadata: {
          bsonType: 'object',
          description: 'Additional metadata'
        },
        createdAt: {
          bsonType: 'date',
          description: 'Creation timestamp'
        }
      }
    }
  }
});

// 6. Cache Storage Collection
db.createCollection('cache_storage', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['key', 'data', 'createdAt'],
      properties: {
        key: {
          bsonType: 'string',
          description: 'Cache key'
        },
        data: {
          description: 'Cached data (any type)'
        },
        ttl: {
          bsonType: 'number',
          minimum: 0,
          description: 'Time to live in seconds'
        },
        tags: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'Cache tags for bulk operations'
        },
        createdAt: {
          bsonType: 'date',
          description: 'Creation timestamp'
        },
        expiresAt: {
          bsonType: 'date',
          description: 'Expiration timestamp'
        }
      }
    }
  }
});

// 7. System Metrics Collection
db.createCollection('system_metrics', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['metricName', 'value', 'timestamp'],
      properties: {
        metricName: {
          bsonType: 'string',
          description: 'Name of the metric'
        },
        value: {
          bsonType: 'number',
          description: 'Metric value'
        },
        unit: {
          bsonType: 'string',
          description: 'Unit of measurement'
        },
        dimensions: {
          bsonType: 'object',
          description: 'Metric dimensions/tags'
        },
        service: {
          bsonType: 'string',
          description: 'Service that generated the metric'
        },
        host: {
          bsonType: 'string',
          description: 'Host that generated the metric'
        },
        timestamp: {
          bsonType: 'date',
          description: 'Metric timestamp'
        }
      }
    }
  }
});

// 8. User Preferences Collection
db.createCollection('user_preferences', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['userId', 'preferences', 'updatedAt'],
      properties: {
        userId: {
          bsonType: 'string',
          description: 'User ID'
        },
        preferences: {
          bsonType: 'object',
          description: 'User preference settings'
        },
        category: {
          bsonType: 'string',
          description: 'Preference category'
        },
        version: {
          bsonType: 'string',
          description: 'Preferences schema version'
        },
        updatedAt: {
          bsonType: 'date',
          description: 'Last update timestamp'
        }
      }
    }
  }
});

print('MongoDB initialization completed successfully!');
print('Created database: finclick_ai');
print('Created user: finclick_app');
print('Created collections with validation schemas:');
print('  - documents');
print('  - analysis_results');
print('  - user_activity_logs');
print('  - file_processing_queue');
print('  - ml_training_data');
print('  - cache_storage');
print('  - system_metrics');
print('  - user_preferences');