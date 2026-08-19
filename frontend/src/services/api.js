const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  return readResponse(await fetch(`${API_URL}/api/assessment`, { method: 'POST', body: form }));
}

export async function fetchApplications() {
  return readResponse(await fetch(`${API_URL}/api/applications`));
}

export async function fetchDashboard() {
  return readResponse(await fetch(`${API_URL}/api/dashboard`));
}
