const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
const API_URL = configuredApiUrl
  ? configuredApiUrl.replace(/\/$/, '')
  : (import.meta.env.DEV ? 'http://127.0.0.1:8000' : null);

function ensureApiUrl() {
  if (!API_URL) {
    throw new Error(
      'Production API is not configured. Set VITE_API_URL in Vercel Environment Variables and redeploy the frontend.',
    );
  }

  return API_URL;
}

function apiUrl(path) {
  return `${ensureApiUrl()}${path}`;
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'The assessment could not be completed.');
  return data;
}

export async function createAssessment(applicant, application, creditFile) {
  const form = new FormData();
  form.append('applicant', JSON.stringify(applicant));
  form.append('application', JSON.stringify(application));
  form.append('credit_report', creditFile);
  return readResponse(await fetch(apiUrl('/api/assessment'), { method: 'POST', body: form }));
}

export async function fetchApplications() {
  return readResponse(await fetch(apiUrl('/api/applications')));
}

export async function fetchDashboard() {
  return readResponse(await fetch(apiUrl('/api/dashboard')));
}
