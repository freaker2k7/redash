import { axios } from "@/services/axios";

const AI = {
  types: () => axios.get(`api/ai/types`),
  get: ({ model }) => axios.get(`api/ai/${model}`),
};

export default AI;
