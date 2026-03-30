const BASE = '/api';

async function get(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  coins:            ()             => get('/coins'),
  coinNames:        ()             => get('/coin-names'),
  coinHistory:      (name, from, to)       => get(`/coin-history?name=${encodeURIComponent(name)}&from=${from}&to=${to}`),
  coinHistoryMulti: (names, from, to)      => get(`/coin-history-multi?names=${names.map(encodeURIComponent).join(',')}&from=${from}&to=${to}`),
  hardware:         ()             => get('/hardware'),
  pools:            ()             => get('/pools'),
  poolStats:        (tag)          => get(tag ? `/pool-stats?tag=${encodeURIComponent(tag)}` : '/pool-stats'),
  poolTags:         ()             => get('/pool-tags'),
  poolNames:        (tag)          => get(tag ? `/pool-names?tag=${encodeURIComponent(tag)}` : '/pool-names'),
  poolHistory:      (name, tag, from, to) => get(`/pool-history?name=${encodeURIComponent(name)}${tag ? `&tag=${encodeURIComponent(tag)}` : ''}${from ? `&from=${from}` : ''}${to ? `&to=${to}` : ''}`),
  aggregatorStatus: ()             => get('/aggregator-status'),
  apiHistory:       (api_name, success, limit, from, to) => {
    const params = new URLSearchParams();
    if (api_name) params.set('api_name', api_name);
    if (success !== undefined && success !== null) params.set('success', success);
    if (limit)    params.set('limit', limit);
    if (from)     params.set('from', from);
    if (to)       params.set('to', to);
    const qs = params.toString();
    return get('/api-history' + (qs ? '?' + qs : ''));
  },
  apiHistoryNames:  ()             => get('/api-history-names'),
};
