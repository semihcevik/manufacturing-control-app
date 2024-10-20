import axios from 'axios';
import { BASE_URL } from '../config';

axios.defaults.baseURL = BASE_URL;
axios.defaults.headers.post['Content-Type'] = 'application/json';

export const fetchPlaneList = async (token) => {
  try {
    const response = await axios.get('/plane/list', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = response.data;
    if (data.status) {
      return data.data.sort((a, b) => a.plane_id - b.plane_id); // Sort the planes
    } else {
      throw new Error('No plane data available');
    }
  } catch (error) {
    throw new Error('Failed to fetch plane data');
  }
};


export const assemblePlane = async (planeId, token) => {
  try {
    const response = await axios.post(
      '/plane/create',
      { plane_id: planeId },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error('Failed to assemble the plane');
  }
};


export const recyclePlane = async (planeId, token) => {
  try {
    const response = await axios.delete('/plane/recycle', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      data: { plane_id: planeId },
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to recycle the plane');
  }
};


export const fetchAssemblyHistory = async (token) => {
  try {
    const response = await axios.get('/plane/assemble-history', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = response.data;
    if (data.status) {
      return data.data;
    } else {
      throw new Error('No assembly history data available');
    }
  } catch (error) {
    throw new Error('Failed to fetch assembly history data');
  }
};