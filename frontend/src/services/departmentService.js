import axios from 'axios';
import { BASE_URL } from '../config';

axios.defaults.baseURL = BASE_URL;

export const getDepartmentList = async (token) => {
  try {
    const response = await axios.get('/department/list', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data; // Returns the department data
  } catch (error) {
    throw new Error('Failed to fetch department information');
  }
};
