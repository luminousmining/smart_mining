const BASE = '/api';

async function get(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  coins:            ()             => get('/coins'),
  coinNames:        ()             => get('/coin-names'),
  coinHistory:      (name, range)  => get(`/coin-history?name=${encodeURIComponent(name)}&range=${range}`),
  coinHistoryMulti: (names, range) => get(`/coin-history-multi?names=${names.map(encodeURIComponent).join(',')}&range=${range}`),
  hardware:         ()             => get('/hardware'),
  pools:            ()             => get('/pools'),
  poolStats:        (tag)          => get(tag ? `/pool-stats?tag=${encodeURIComponent(tag)}` : '/pool-stats'),
  poolTags:         ()             => get('/pool-tags'),
  poolNames:        (tag)          => get(tag ? `/pool-names?tag=${encodeURIComponent(tag)}` : '/pool-names'),
  poolHistory:      (name, tag)    => get(`/pool-history?name=${encodeURIComponent(name)}${tag ? `&tag=${encodeURIComponent(tag)}` : ''}`),
};
