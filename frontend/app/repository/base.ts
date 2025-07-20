const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BACKEND_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error: ${response.status} - ${errorText}`);
  }

  return response.json();
}

export async function uploadRequest<T>(
  endpoint: string,
  formData: FormData,
  onProgress?: (progress: number) => void
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          onProgress(progress);
        }
      });
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          resolve(data);
        } catch (error) {
          reject(new Error('Failed to parse response'));
        }
      } else {
        reject(new Error(`Upload failed: ${xhr.status} - ${xhr.responseText}`));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed'));
    });

    xhr.open('POST', `${BACKEND_URL}${endpoint}`);
    xhr.send(formData);
  });
}

export async function streamRequest(endpoint: string): Promise<Response> {
  const url = `${BACKEND_URL}${endpoint}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Stream request failed: ${response.status}`);
  }
  
  return response;
}