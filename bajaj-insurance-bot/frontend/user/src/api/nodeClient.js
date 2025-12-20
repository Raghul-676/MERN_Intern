import axios from "axios";

export const nodeApi = axios.create({
  baseURL: "http://localhost:5000",
});
