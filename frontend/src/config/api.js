const rawBase = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
console.log('API Base URL:', rawBase);
export const API_BASE = rawBase.replace(/\/$/, '');
export const apiJoin = (path) => {
  if (!path.startsWith('/')) path = '/' + path;
  return `${API_BASE}${path}`;
};
