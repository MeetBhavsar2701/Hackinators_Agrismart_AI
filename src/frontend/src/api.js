import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const predictImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/predict`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting image:', error);
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to predict image');
    }
    throw new Error('Network error. Is the backend running?');
  }
};
