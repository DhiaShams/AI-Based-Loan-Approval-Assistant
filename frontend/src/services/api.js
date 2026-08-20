const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
const API_URL = configuredApiUrl ? configuredApiUrl.replace(/\/$/, '') : null;

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

async function readResponse(response, requestDetails = {}) {
  const body = await response.text();
  let data = {};
  try {
    data = JSON.parse(body || '{}');
  } catch {
    data = {};
  }
  if (!response.ok) {
    if (requestDetails.label) {
      console.error(`[${requestDetails.label}] HTTP error`, {
        url: requestDetails.url,
        status: response.status,
        body,
      });
    }
    throw new Error(data.detail || 'The assessment could not be completed.');
  }
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

export async function fetchFairness() {
  const url = apiUrl('/api/fairness');
  try {
    return await readResponse(await fetch(url), { label: 'Fairness API', url });
  } catch (error) {
    console.error('[Fairness API] Request failed', { url, error: error.message });
    throw error;
  }
}
