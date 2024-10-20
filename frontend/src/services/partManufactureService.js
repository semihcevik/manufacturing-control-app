// src/services/partManufactureService.js

import axios from 'axios';
import { BASE_URL } from '../config';

axios.defaults.baseURL = BASE_URL;
axios.defaults.headers.post['Content-Type'] = 'application/json';

export const fetchPartList = async (token) => {
  try {
    const response = await axios.get('/part/list', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = response.data;

    // Check the response structure
    console.log('Response Data:', data);

    if (data.status && data.data) {
      return {
        part_id: data.part_id, 
        data: data.data
      };
    } else {
      throw new Error('No part data available');
    }
  } catch (error) {
    console.error('Error fetching part data:', error);
    throw new Error('Failed to fetch part data');
  }
};

export const addPart = async (partId, planeId, token) => {
  try {
    const response = await axios.post(
      '/part/create',
      { part_id: partId, plane_id: planeId },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error('Failed to add the part');
  }
};

export const recyclePart = async (partId, planeId, token) => {
  try {
    const response = await axios.delete('/part/recycle', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      data: { part_id: partId, plane_id: planeId },
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to recycle the part');
  }
};
