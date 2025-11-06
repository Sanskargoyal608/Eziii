const API_BASE_URL = 'http://127.0.0.1:8000/api';
const PORTAL_BASE_URL = 'http://127.0.0.1:8000';

export const apiFetch = async (url, options = {}) => {
    const token = localStorage.getItem('accessToken');
    
    const headers = {
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const isPortalUrl = url.startsWith('/portal');
    const baseUrl = isPortalUrl ? PORTAL_BASE_URL : API_BASE_URL;

    const response = await fetch(`${baseUrl}${url}`, {
        ...options,
        headers,
    });

    if (response.status === 401 && !isPortalUrl) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login'; 
        throw new Error('Session expired. Please log in again.');
    }

    return response;
};