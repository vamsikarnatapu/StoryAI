import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createStory, listStories, Story } from '../services/api';
import { motion } from 'framer-motion';

export const Home: React.FC = () => {
    const [theme, setTheme] = useState('');
    const [stories, setStories] = useState<Story[]>([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        loadStories();
    }, []);

    const loadStories = async () => {
        try {
            const data = await listStories();
            setStories(data);
        } catch (error) {
            console.error("Failed to load stories", error);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!theme) return;
        setLoading(true);
        try {
            const story = await createStory(theme);
            navigate(`/story/${story.id}`);
        } catch (error) {
            console.error("Failed to create story", error);
            alert("Failed to create story. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 p-8 text-white">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-5xl font-bold mb-8 text-center drop-shadow-lg">MyStory AI</h1>

                <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 mb-12 shadow-xl">
                    <h2 className="text-2xl font-semibold mb-4">Create a New Story</h2>
                    <form onSubmit={handleCreate} className="flex gap-4">
                        <input
                            type="text"
                            value={theme}
                            onChange={(e) => setTheme(e.target.value)}
                            placeholder="Enter a theme (e.g., 'A brave bunny in space')"
                            className="flex-1 p-4 rounded-lg bg-white/20 placeholder-white/70 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-yellow-400 hover:bg-yellow-300 text-indigo-900 font-bold py-4 px-8 rounded-lg transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Generating...' : 'Create Magic'}
                        </button>
                    </form>
                </div>

                <h2 className="text-3xl font-bold mb-6">Your Library</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {stories.map((story) => (
                        <Link to={`/story/${story.id}`} key={story.id}>
                            <motion.div
                                whileHover={{ scale: 1.05 }}
                                className="bg-white/10 backdrop-blur-sm rounded-xl p-6 cursor-pointer hover:bg-white/20 transition-colors border border-white/10"
                            >
                                <h3 className="text-xl font-bold mb-2">{story.title}</h3>
                                <p className="text-white/70 text-sm">{new Date().toLocaleDateString()}</p>
                            </motion.div>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
};
