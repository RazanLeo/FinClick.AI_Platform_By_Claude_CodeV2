-- Redis Lua Scripts for FinClick.AI Platform
-- These scripts provide atomic operations for complex Redis operations

-- Script 1: Session Management
-- Creates or updates a user session with atomic operations
local function create_or_update_session(session_key, user_id, session_data, ttl)
    local session_info = {
        user_id = user_id,
        created_at = redis.call('TIME')[1],
        last_accessed = redis.call('TIME')[1],
        data = session_data
    }

    -- Set session data
    redis.call('HMSET', session_key,
        'user_id', session_info.user_id,
        'created_at', session_info.created_at,
        'last_accessed', session_info.last_accessed,
        'data', cjson.encode(session_info.data))

    -- Set TTL
    redis.call('EXPIRE', session_key, ttl)

    -- Update user's active sessions list
    local user_sessions_key = 'user_sessions:' .. user_id
    redis.call('SADD', user_sessions_key, session_key)
    redis.call('EXPIRE', user_sessions_key, ttl + 300) -- Extra 5 minutes

    return session_info.created_at
end

-- Script 2: Rate Limiting with Sliding Window
-- Implements sliding window rate limiting
local function rate_limit_sliding_window(key, limit, window_size)
    local current_time = redis.call('TIME')
    local current_timestamp = current_time[1]
    local window_start = current_timestamp - window_size

    -- Remove expired entries
    redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

    -- Count current requests
    local current_requests = redis.call('ZCARD', key)

    if current_requests < limit then
        -- Add current request
        redis.call('ZADD', key, current_timestamp, current_timestamp .. ':' .. current_time[2])
        redis.call('EXPIRE', key, window_size + 1)
        return {1, limit - current_requests - 1}
    else
        return {0, 0}
    end
end

-- Script 3: Cache with Automatic Refresh
-- Implements cache-aside pattern with automatic refresh
local function cache_with_refresh(cache_key, lock_key, ttl, refresh_threshold)
    local cached_value = redis.call('GET', cache_key)
    local cache_ttl = redis.call('TTL', cache_key)

    if cached_value then
        -- Check if cache needs refresh
        if cache_ttl < refresh_threshold then
            -- Try to acquire refresh lock
            local lock_acquired = redis.call('SET', lock_key, '1', 'NX', 'EX', 30)
            if lock_acquired then
                return {'hit', cached_value, 'refresh_needed'}
            else
                return {'hit', cached_value, 'refreshing'}
            end
        else
            return {'hit', cached_value, 'fresh'}
        end
    else
        -- Cache miss - try to acquire lock to prevent thundering herd
        local lock_acquired = redis.call('SET', lock_key, '1', 'NX', 'EX', 30)
        if lock_acquired then
            return {'miss', nil, 'lock_acquired'}
        else
            return {'miss', nil, 'lock_exists'}
        end
    end
end

-- Script 4: Notification Queue Management
-- Manages notification queues with priority and deduplication
local function enqueue_notification(queue_key, notification_id, priority, payload, dedup_key)
    -- Check for duplicates if dedup_key provided
    if dedup_key then
        local dedup_full_key = queue_key .. ':dedup:' .. dedup_key
        local exists = redis.call('EXISTS', dedup_full_key)
        if exists == 1 then
            return 0 -- Duplicate notification
        end
        -- Set deduplication marker with 1-hour expiry
        redis.call('SETEX', dedup_full_key, 3600, notification_id)
    end

    -- Add to priority queue
    local score = priority * 1000000 + redis.call('TIME')[1]
    redis.call('ZADD', queue_key, score, notification_id)

    -- Store notification payload
    local payload_key = queue_key .. ':payload:' .. notification_id
    redis.call('SETEX', payload_key, 86400, payload) -- 24 hours expiry

    return 1 -- Successfully enqueued
end

-- Script 5: Analytics Counter with Time Windows
-- Implements counters for analytics with multiple time windows
local function increment_analytics_counter(base_key, increment, timestamp)
    local current_time = timestamp or redis.call('TIME')[1]

    -- Define time windows: minute, hour, day, week, month
    local windows = {
        {suffix = 'min', duration = 60, format = '%Y%m%d%H%M'},
        {suffix = 'hour', duration = 3600, format = '%Y%m%d%H'},
        {suffix = 'day', duration = 86400, format = '%Y%m%d'},
        {suffix = 'week', duration = 604800, format = '%Y%W'},
        {suffix = 'month', duration = 2592000, format = '%Y%m'}
    }

    local results = {}

    for _, window in ipairs(windows) do
        -- Calculate time bucket
        local bucket = os.date(window.format, current_time)
        local key = base_key .. ':' .. window.suffix .. ':' .. bucket

        -- Increment counter
        local new_value = redis.call('INCRBY', key, increment)

        -- Set expiry (2x window duration for safety)
        redis.call('EXPIRE', key, window.duration * 2)

        results[window.suffix] = new_value
    end

    return results
end

-- Script 6: Financial Data Cache Invalidation
-- Invalidates related financial data caches when data changes
local function invalidate_financial_caches(user_id, account_id, category_patterns)
    local patterns = {
        'cache:user:' .. user_id .. ':*',
        'cache:account:' .. account_id .. ':*',
        'cache:financial_summary:' .. user_id,
        'cache:analytics:' .. user_id .. ':*'
    }

    -- Add custom patterns if provided
    if category_patterns then
        for _, pattern in ipairs(category_patterns) do
            table.insert(patterns, pattern)
        end
    end

    local deleted_count = 0

    for _, pattern in ipairs(patterns) do
        local keys = redis.call('KEYS', pattern)
        if #keys > 0 then
            deleted_count = deleted_count + redis.call('DEL', unpack(keys))
        end
    end

    return deleted_count
end

-- Script 7: Leaderboard with Score Decay
-- Implements leaderboard with time-based score decay
local function update_leaderboard_with_decay(leaderboard_key, member, score, decay_rate, current_time)
    local time = current_time or redis.call('TIME')[1]

    -- Get current score and last update time
    local member_data_key = leaderboard_key .. ':member:' .. member
    local last_score = redis.call('HGET', member_data_key, 'score') or 0
    local last_update = redis.call('HGET', member_data_key, 'last_update') or time

    -- Calculate decay
    local time_diff = time - last_update
    local decayed_score = last_score * math.exp(-decay_rate * time_diff)

    -- Add new score
    local new_score = decayed_score + score

    -- Update leaderboard
    redis.call('ZADD', leaderboard_key, new_score, member)

    -- Store member data
    redis.call('HMSET', member_data_key,
        'score', new_score,
        'last_update', time,
        'total_score', (redis.call('HGET', member_data_key, 'total_score') or 0) + score)

    -- Set expiry for member data
    redis.call('EXPIRE', member_data_key, 2592000) -- 30 days

    return new_score
end

-- Script 8: Distributed Lock with Automatic Renewal
-- Implements distributed lock with heartbeat for long operations
local function acquire_lock_with_renewal(lock_key, client_id, ttl, renewal_interval)
    -- Try to acquire lock
    local acquired = redis.call('SET', lock_key, client_id, 'NX', 'EX', ttl)

    if acquired then
        -- Set up renewal tracking
        local renewal_key = lock_key .. ':renewal'
        redis.call('HSET', renewal_key, 'client_id', client_id, 'interval', renewal_interval, 'last_renewal', redis.call('TIME')[1])
        redis.call('EXPIRE', renewal_key, ttl + 10)

        return {1, 'acquired'}
    else
        -- Check if lock belongs to same client
        local current_owner = redis.call('GET', lock_key)
        if current_owner == client_id then
            -- Extend the lock
            redis.call('EXPIRE', lock_key, ttl)
            local renewal_key = lock_key .. ':renewal'
            redis.call('HSET', renewal_key, 'last_renewal', redis.call('TIME')[1])
            redis.call('EXPIRE', renewal_key, ttl + 10)
            return {1, 'extended'}
        else
            return {0, 'locked_by_other'}
        end
    end
end

-- Script Registry
-- Register scripts for easy access
local scripts = {
    session_management = create_or_update_session,
    rate_limiting = rate_limit_sliding_window,
    cache_refresh = cache_with_refresh,
    notification_queue = enqueue_notification,
    analytics_counter = increment_analytics_counter,
    cache_invalidation = invalidate_financial_caches,
    leaderboard_decay = update_leaderboard_with_decay,
    distributed_lock = acquire_lock_with_renewal
}

-- Export for use
return scripts