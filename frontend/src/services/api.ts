import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
});

export interface Page {
    id: number;
    page_number: number;
    text_content: string;
    image_url: string;
    audio_url: string;
}

export interface Story {
    id: number;
    title: string;
    theme: string;
    pages: Page[];
}

export const createStory = async (theme: string) => {
    const response = await api.post<Story>('/stories/', { theme });
    return response.data;
};

export const getStory = async (id: number) => {
    const response = await api.get<Story>(`/stories/${id}`);
    return response.data;
};

export const listStories = async () => {
    const response = await api.get<Story[]>('/stories/');
    return response.data;
};

export const generateAudio = async (storyId: number) => {
    const response = await api.post<Story>(`/stories/${storyId}/generate-audio`);
    return response.data;
};
