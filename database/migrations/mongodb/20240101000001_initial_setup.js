// Migration: Initial MongoDB Setup
// Created: 2024-01-01
// Version: 20240101000001_initial_setup
// Description: Creates initial MongoDB collections with validation schemas

// Switch to the FinClick.AI database
db = db.getSiblingDB('finclick_ai');

print('Running migration: Initial MongoDB Setup');

try {
    // Create application user if not exists
    try {
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
        print('Created application user: finclick_app');
    } catch (error) {
        if (error.code !== 11000) { // User already exists
            throw error;
        }
        print('User finclick_app already exists');
    }

    // 1. Documents Collection
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
                    uploadedAt: {
                        bsonType: 'date',
                        description: 'Upload timestamp'
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
                    result: {
                        bsonType: 'object',
                        description: 'Analysis results'
                    },
                    createdAt: {
                        bsonType: 'date',
                        description: 'Creation timestamp'
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
                    action: {
                        bsonType: 'string',
                        description: 'Action performed by user'
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
                    createdAt: {
                        bsonType: 'date',
                        description: 'Queue entry creation time'
                    }
                }
            }
        }
    });

    // 5. Cache Storage Collection
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
                    createdAt: {
                        bsonType: 'date',
                        description: 'Creation timestamp'
                    }
                }
            }
        }
    });

    // Create basic indexes
    print('Creating basic indexes...');

    // Documents indexes
    db.documents.createIndex({ userId: 1 });
    db.documents.createIndex({ fileType: 1 });
    db.documents.createIndex({ uploadedAt: -1 });
    db.documents.createIndex({ userId: 1, uploadedAt: -1 });

    // Analysis results indexes
    db.analysis_results.createIndex({ userId: 1 });
    db.analysis_results.createIndex({ analysisType: 1 });
    db.analysis_results.createIndex({ createdAt: -1 });
    db.analysis_results.createIndex({ userId: 1, analysisType: 1 });

    // User activity logs indexes
    db.user_activity_logs.createIndex({ userId: 1 });
    db.user_activity_logs.createIndex({ timestamp: -1 });
    db.user_activity_logs.createIndex({ userId: 1, timestamp: -1 });

    // File processing queue indexes
    db.file_processing_queue.createIndex({ documentId: 1 });
    db.file_processing_queue.createIndex({ status: 1 });
    db.file_processing_queue.createIndex({ processingType: 1 });

    // Cache storage indexes
    db.cache_storage.createIndex({ key: 1 }, { unique: true });
    db.cache_storage.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0, sparse: true });

    print('Initial MongoDB setup completed successfully');

} catch (error) {
    print('Migration failed: ' + error.message);
    throw error;
}