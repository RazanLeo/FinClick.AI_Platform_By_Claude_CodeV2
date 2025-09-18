// MongoDB Collections Configuration for FinClick.AI Platform
// This script contains collection configurations, sharding setup, and optimization settings

// Switch to the FinClick.AI database
db = db.getSiblingDB('finclick_ai');

print('Configuring MongoDB collections for FinClick.AI...');

// 1. Configure Collection Sharding (for MongoDB Sharded Clusters)
// Note: These commands should be run on mongos in a sharded environment

const configureSharding = function() {
  print('Configuring sharding for collections...');

  // Enable sharding for the database
  // sh.enableSharding('finclick_ai');

  // Shard key configurations for large collections
  const shardConfigs = [
    {
      collection: 'finclick_ai.user_activity_logs',
      key: { userId: 1, timestamp: 1 },
      reason: 'Distribute user activity by user and time for optimal performance'
    },
    {
      collection: 'finclick_ai.documents',
      key: { userId: 1, uploadedAt: 1 },
      reason: 'Distribute documents by user and upload time'
    },
    {
      collection: 'finclick_ai.analysis_results',
      key: { userId: 1, createdAt: 1 },
      reason: 'Distribute analysis results by user and creation time'
    },
    {
      collection: 'finclick_ai.system_metrics',
      key: { service: 1, timestamp: 1 },
      reason: 'Distribute metrics by service and time'
    }
  ];

  shardConfigs.forEach(config => {
    print(`Sharding ${config.collection} with key ${JSON.stringify(config.key)}`);
    print(`Reason: ${config.reason}`);
    // sh.shardCollection(config.collection, config.key);
  });
};

// 2. Configure Collection Options and Optimization
const configureCollectionOptions = function() {
  print('Configuring collection options...');

  // Set up capped collections for high-volume logs
  db.createCollection('real_time_logs', {
    capped: true,
    size: 100000000, // 100MB
    max: 1000000 // 1M documents
  });

  // Configure time series collections (MongoDB 5.0+)
  try {
    db.createCollection('time_series_metrics', {
      timeseries: {
        timeField: 'timestamp',
        metaField: 'metadata',
        granularity: 'minutes'
      }
    });
    print('Time series collection created for metrics');
  } catch (e) {
    print('Time series collections not supported in this MongoDB version');
  }

  // Configure collection validation rules
  const validationRules = {
    documents: {
      validator: {
        $jsonSchema: {
          bsonType: 'object',
          required: ['userId', 'fileName', 'fileType', 'uploadedAt'],
          properties: {
            fileSize: { bsonType: 'number', minimum: 0, maximum: 104857600 }, // 100MB max
            userId: { bsonType: 'string', pattern: '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$' }
          }
        }
      },
      validationLevel: 'strict',
      validationAction: 'error'
    }
  };

  // Apply validation rules
  Object.keys(validationRules).forEach(collectionName => {
    try {
      db.runCommand({
        collMod: collectionName,
        validator: validationRules[collectionName].validator,
        validationLevel: validationRules[collectionName].validationLevel,
        validationAction: validationRules[collectionName].validationAction
      });
      print(`Validation rules applied to ${collectionName}`);
    } catch (e) {
      print(`Failed to apply validation to ${collectionName}: ${e.message}`);
    }
  });
};

// 3. Set up Change Streams for Real-time Processing
const setupChangeStreams = function() {
  print('Setting up change stream configurations...');

  // This is typically done in application code, but we document the configurations here
  const changeStreamConfigs = {
    documents: {
      pipeline: [
        { $match: { 'fullDocument.processingStatus': 'pending' } }
      ],
      fullDocument: 'updateLookup'
    },
    file_processing_queue: {
      pipeline: [
        { $match: { operationType: { $in: ['insert', 'update'] } } }
      ],
      fullDocument: 'updateLookup'
    },
    user_activity_logs: {
      pipeline: [
        { $match: { 'fullDocument.action': { $in: ['login', 'logout', 'suspicious_activity'] } } }
      ],
      fullDocument: 'updateLookup'
    }
  };

  print('Change stream configurations documented for:');
  Object.keys(changeStreamConfigs).forEach(collection => {
    print(`  - ${collection}: ${JSON.stringify(changeStreamConfigs[collection].pipeline)}`);
  });
};

// 4. Configure GridFS for Large File Storage
const configureGridFS = function() {
  print('Configuring GridFS for large file storage...');

  // GridFS collections are created automatically, but we can set up indexes
  db.fs.files.createIndex({ filename: 1 });
  db.fs.files.createIndex({ uploadDate: -1 });
  db.fs.files.createIndex({ 'metadata.userId': 1 });
  db.fs.files.createIndex({ 'metadata.category': 1 });
  db.fs.files.createIndex({ length: 1 });

  db.fs.chunks.createIndex({ files_id: 1, n: 1 }, { unique: true });

  print('GridFS indexes created for file storage optimization');
};

// 5. Set up Data Lifecycle Management
const configureDataLifecycle = function() {
  print('Configuring data lifecycle management...');

  // TTL (Time To Live) indexes for automatic data cleanup
  const ttlConfigs = [
    {
      collection: 'user_activity_logs',
      field: 'timestamp',
      expireAfterSeconds: 7776000, // 90 days
      reason: 'Auto-cleanup old activity logs'
    },
    {
      collection: 'system_metrics',
      field: 'timestamp',
      expireAfterSeconds: 2592000, // 30 days
      reason: 'Auto-cleanup old system metrics'
    },
    {
      collection: 'cache_storage',
      field: 'expiresAt',
      expireAfterSeconds: 0, // Use expiresAt field value
      reason: 'Auto-cleanup expired cache entries'
    },
    {
      collection: 'analysis_results',
      field: 'expiresAt',
      expireAfterSeconds: 0, // Use expiresAt field value
      reason: 'Auto-cleanup expired analysis results'
    }
  ];

  ttlConfigs.forEach(config => {
    try {
      const indexSpec = {};
      indexSpec[config.field] = 1;
      db[config.collection].createIndex(indexSpec, { expireAfterSeconds: config.expireAfterSeconds });
      print(`TTL index created for ${config.collection}.${config.field} - ${config.reason}`);
    } catch (e) {
      print(`Failed to create TTL index for ${config.collection}: ${e.message}`);
    }
  });
};

// 6. Configure Read Preferences and Write Concerns
const configureReadWritePreferences = function() {
  print('Configuring read/write preferences...');

  // Collection-specific read/write configurations
  const collections = [
    {
      name: 'documents',
      readPreference: 'secondaryPreferred',
      writeConcern: { w: 'majority', j: true }
    },
    {
      name: 'user_activity_logs',
      readPreference: 'secondary',
      writeConcern: { w: 1, j: false } // Fast writes for high-volume logs
    },
    {
      name: 'analysis_results',
      readPreference: 'primary',
      writeConcern: { w: 'majority', j: true }
    },
    {
      name: 'file_processing_queue',
      readPreference: 'primary',
      writeConcern: { w: 'majority', j: true }
    }
  ];

  print('Read/write preference configurations documented:');
  collections.forEach(config => {
    print(`  - ${config.name}:`);
    print(`    Read Preference: ${config.readPreference}`);
    print(`    Write Concern: ${JSON.stringify(config.writeConcern)}`);
  });
};

// 7. Set up Aggregation Pipeline Optimization
const configureAggregationOptimization = function() {
  print('Setting up aggregation pipeline optimizations...');

  // Common aggregation pipelines for optimization
  const commonPipelines = {
    userActivitySummary: [
      { $match: { userId: 'USER_ID_PLACEHOLDER', timestamp: { $gte: 'DATE_PLACEHOLDER' } } },
      { $group: { _id: '$action', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ],
    documentStatsByCategory: [
      { $match: { userId: 'USER_ID_PLACEHOLDER' } },
      { $group: { _id: '$category', count: { $sum: 1 }, totalSize: { $sum: '$fileSize' } } },
      { $sort: { count: -1 } }
    ],
    analysisResultsTrends: [
      { $match: { userId: 'USER_ID_PLACEHOLDER', analysisType: 'TYPE_PLACEHOLDER' } },
      { $group: { _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } }, avgConfidence: { $avg: '$confidence' } } },
      { $sort: { _id: 1 } }
    ]
  };

  print('Common aggregation pipelines documented for optimization:');
  Object.keys(commonPipelines).forEach(pipelineName => {
    print(`  - ${pipelineName}: ${commonPipelines[pipelineName].length} stages`);
  });
};

// 8. Monitor Collection Performance
const setupPerformanceMonitoring = function() {
  print('Setting up performance monitoring...');

  // Collection statistics
  const collections = ['documents', 'analysis_results', 'user_activity_logs', 'file_processing_queue'];

  collections.forEach(collectionName => {
    try {
      const stats = db[collectionName].stats();
      print(`${collectionName} collection stats:`);
      print(`  - Documents: ${stats.count}`);
      print(`  - Size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
      print(`  - Average document size: ${(stats.avgObjSize / 1024).toFixed(2)} KB`);
      print(`  - Indexes: ${stats.nindexes}`);
      print(`  - Index size: ${(stats.totalIndexSize / 1024 / 1024).toFixed(2)} MB`);
    } catch (e) {
      print(`Collection ${collectionName} does not exist yet`);
    }
  });
};

// Execute all configuration functions
try {
  configureCollectionOptions();
  configureGridFS();
  configureDataLifecycle();
  configureReadWritePreferences();
  configureAggregationOptimization();
  setupPerformanceMonitoring();
  setupChangeStreams();

  print('\nMongoDB collections configuration completed successfully!');
  print('\nNote: Sharding configuration is commented out and should be');
  print('executed manually in a sharded cluster environment.');

} catch (e) {
  print(`Configuration error: ${e.message}`);
}

// Helper function to check collection health
const checkCollectionHealth = function() {
  print('\nChecking collection health...');

  const collections = db.listCollectionNames();
  collections.forEach(collectionName => {
    try {
      const count = db[collectionName].countDocuments();
      const indexCount = db[collectionName].getIndexes().length;
      print(`${collectionName}: ${count} documents, ${indexCount} indexes`);
    } catch (e) {
      print(`Error checking ${collectionName}: ${e.message}`);
    }
  });
};

checkCollectionHealth();