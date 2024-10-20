import axios from 'axios';
import { BASE_URL } from '../config';

axios.defaults.baseURL = BASE_URL;
axios.defaults.headers.post['Content-Type'] = 'application/json';

export const login = async (username, password) => {
  try {
    const response = await axios.post('/personnel/login/', { username, password });
    return response.data; // Returns the token data
  } catch (error) {
    if (error.response && error.response.status === 401) {
      throw new Error('Username or password is incorrect');
    } else {
      throw new Error('An error occurred during login. Please try again.');
    }
  }
};
