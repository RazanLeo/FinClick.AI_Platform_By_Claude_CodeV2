// MongoDB Indexes Creation Script for FinClick.AI Platform
// This script creates optimized indexes for all collections

// Switch to the FinClick.AI database
db = db.getSiblingDB('finclick_ai');

print('Creating indexes for FinClick.AI database...');

// 1. Documents Collection Indexes
print('Creating indexes for documents collection...');
db.documents.createIndex({ userId: 1 });
db.documents.createIndex({ fileName: 'text' });
db.documents.createIndex({ fileType: 1 });
db.documents.createIndex({ category: 1 });
db.documents.createIndex({ uploadedAt: -1 });
db.documents.createIndex({ tags: 1 });
db.documents.createIndex({ userId: 1, category: 1 });
db.documents.createIndex({ userId: 1, uploadedAt: -1 });
db.documents.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
db.documents.createIndex({
  fileName: 'text',
  'metadata.description': 'text',
  tags: 'text'
}, {
  name: 'text_search_index',
  weights: {
    fileName: 10,
    'metadata.description': 5,
    tags: 3
  }
});

// 2. Analysis Results Collection Indexes
print('Creating indexes for analysis_results collection...');
db.analysis_results.createIndex({ userId: 1 });
db.analysis_results.createIndex({ analysisType: 1 });
db.analysis_results.createIndex({ createdAt: -1 });
db.analysis_results.createIndex({ confidence: -1 });
db.analysis_results.createIndex({ userId: 1, analysisType: 1 });
db.analysis_results.createIndex({ userId: 1, createdAt: -1 });
db.analysis_results.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
db.analysis_results.createIndex({ tags: 1 });
db.analysis_results.createIndex({
  'result.insights': 1,
  'result.recommendations': 1
}, { sparse: true });

// 3. User Activity Logs Collection Indexes
print('Creating indexes for user_activity_logs collection...');
db.user_activity_logs.createIndex({ userId: 1 });
db.user_activity_logs.createIndex({ sessionId: 1 });
db.user_activity_logs.createIndex({ action: 1 });
db.user_activity_logs.createIndex({ timestamp: -1 });
db.user_activity_logs.createIndex({ userId: 1, timestamp: -1 });
db.user_activity_logs.createIndex({ ipAddress: 1 });
db.user_activity_logs.createIndex({ resource: 1, resourceId: 1 });
db.user_activity_logs.createIndex({
  timestamp: -1
}, {
  expireAfterSeconds: 7776000 // 90 days retention
});
db.user_activity_logs.createIndex({ 'location.country': 1 });
db.user_activity_logs.createIndex({ 'deviceInfo.platform': 1 });

// 4. File Processing Queue Collection Indexes
print('Creating indexes for file_processing_queue collection...');
db.file_processing_queue.createIndex({ documentId: 1 });
db.file_processing_queue.createIndex({ processingType: 1 });
db.file_processing_queue.createIndex({ status: 1 });
db.file_processing_queue.createIndex({ priority: 1, createdAt: 1 });
db.file_processing_queue.createIndex({ status: 1, priority: 1 });
db.file_processing_queue.createIndex({ createdAt: -1 });
db.file_processing_queue.createIndex({
  status: 1,
  processingType: 1,
  priority: 1
});

// 5. ML Training Data Collection Indexes
print('Creating indexes for ml_training_data collection...');
db.ml_training_data.createIndex({ modelType: 1 });
db.ml_training_data.createIndex({ userId: 1 });
db.ml_training_data.createIndex({ createdAt: -1 });
db.ml_training_data.createIndex({ dataSource: 1 });
db.ml_training_data.createIndex({ version: 1 });
db.ml_training_data.createIndex({ isValidated: 1 });
db.ml_training_data.createIndex({ modelType: 1, version: 1 });
db.ml_training_data.createIndex({ userId: 1, modelType: 1 });

// 6. Cache Storage Collection Indexes
print('Creating indexes for cache_storage collection...');
db.cache_storage.createIndex({ key: 1 }, { unique: true });
db.cache_storage.createIndex({ tags: 1 });
db.cache_storage.createIndex({ createdAt: -1 });
db.cache_storage.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// 7. System Metrics Collection Indexes
print('Creating indexes for system_metrics collection...');
db.system_metrics.createIndex({ metricName: 1 });
db.system_metrics.createIndex({ timestamp: -1 });
db.system_metrics.createIndex({ service: 1 });
db.system_metrics.createIndex({ host: 1 });
db.system_metrics.createIndex({ metricName: 1, timestamp: -1 });
db.system_metrics.createIndex({ service: 1, metricName: 1 });
db.system_metrics.createIndex({
  timestamp: -1
}, {
  expireAfterSeconds: 2592000 // 30 days retention
});
db.system_metrics.createIndex({ 'dimensions.environment': 1 });

// 8. User Preferences Collection Indexes
print('Creating indexes for user_preferences collection...');
db.user_preferences.createIndex({ userId: 1 });
db.user_preferences.createIndex({ category: 1 });
db.user_preferences.createIndex({ userId: 1, category: 1 }, { unique: true });
db.user_preferences.createIndex({ updatedAt: -1 });
db.user_preferences.createIndex({ version: 1 });

// Compound indexes for complex queries
print('Creating compound indexes for complex queries...');

// Document search with filters
db.documents.createIndex({
  userId: 1,
  category: 1,
  fileType: 1,
  uploadedAt: -1
});

// Analysis results with confidence filtering
db.analysis_results.createIndex({
  userId: 1,
  analysisType: 1,
  confidence: -1,
  createdAt: -1
});

// User activity with time range and action filtering
db.user_activity_logs.createIndex({
  userId: 1,
  action: 1,
  timestamp: -1
});

// Processing queue priority sorting
db.file_processing_queue.createIndex({
  status: 1,
  priority: 1,
  createdAt: 1
});

// ML data filtering by model and validation status
db.ml_training_data.createIndex({
  modelType: 1,
  isValidated: 1,
  createdAt: -1
});

// System metrics time series queries
db.system_metrics.createIndex({
  service: 1,
  metricName: 1,
  timestamp: -1
});

// Geospatial indexes for location-based queries
print('Creating geospatial indexes...');
db.user_activity_logs.createIndex({ 'location.coordinates': '2dsphere' });

// Partial indexes for specific use cases
print('Creating partial indexes...');

// Index only for encrypted documents
db.documents.createIndex(
  { userId: 1, uploadedAt: -1 },
  {
    partialFilterExpression: { isEncrypted: true },
    name: 'encrypted_documents_index'
  }
);

// Index only for failed processing items
db.file_processing_queue.createIndex(
  { processingType: 1, createdAt: -1 },
  {
    partialFilterExpression: { status: 'failed' },
    name: 'failed_processing_index'
  }
);

// Index only for high-confidence analysis results
db.analysis_results.createIndex(
  { userId: 1, analysisType: 1, createdAt: -1 },
  {
    partialFilterExpression: { confidence: { $gte: 0.8 } },
    name: 'high_confidence_results_index'
  }
);

// Sparse indexes for optional fields
print('Creating sparse indexes...');
db.documents.createIndex({ expiresAt: 1 }, { sparse: true });
db.analysis_results.createIndex({ 'result.score': -1 }, { sparse: true });
db.user_activity_logs.createIndex({ 'location.coordinates': '2dsphere' }, { sparse: true });

// Create collection statistics for query optimization
print('Creating collection statistics...');
db.runCommand({ collStats: 'documents' });
db.runCommand({ collStats: 'analysis_results' });
db.runCommand({ collStats: 'user_activity_logs' });
db.runCommand({ collStats: 'file_processing_queue' });

print('All indexes created successfully!');

// Display created indexes for verification
print('\nIndex summary:');
print('Documents collection indexes:');
db.documents.getIndexes().forEach(index => print('  - ' + index.name));

print('\nAnalysis results collection indexes:');
db.analysis_results.getIndexes().forEach(index => print('  - ' + index.name));

print('\nUser activity logs collection indexes:');
db.user_activity_logs.getIndexes().forEach(index => print('  - ' + index.name));

print('\nFile processing queue collection indexes:');
db.file_processing_queue.getIndexes().forEach(index => print('  - ' + index.name));

print('\nML training data collection indexes:');
db.ml_training_data.getIndexes().forEach(index => print('  - ' + index.name));

print('\nCache storage collection indexes:');
db.cache_storage.getIndexes().forEach(index => print('  - ' + index.name));

print('\nSystem metrics collection indexes:');
db.system_metrics.getIndexes().forEach(index => print('  - ' + index.name));

print('\nUser preferences collection indexes:');
db.user_preferences.getIndexes().forEach(index => print('  - ' + index.name));

print('\nIndex creation completed!');