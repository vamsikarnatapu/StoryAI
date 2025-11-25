import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStory, generateAudio, Story } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';

export const StoryViewer: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [story, setStory] = useState<Story | null>(null);
    const [currentPageIndex, setCurrentPageIndex] = useState(0);

    useEffect(() => {
        if (id) loadStory(parseInt(id));
    }, [id]);

    const loadStory = async (storyId: number) => {
        try {
            const data = await getStory(storyId);
            setStory(data);
        } catch (error) {
            console.error("Failed to load story", error);
        }
    };

    if (!story) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Loading story...</div>;

    if (story.pages.length === 0) {
        return (
            <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white gap-4">
                <p>Story is being generated...</p>
                <button onClick={() => id && loadStory(parseInt(id))} className="px-4 py-2 bg-blue-500 rounded">Refresh</button>
                <Link to="/" className="text-blue-400 hover:underline">Back to Home</Link>
            </div>
        );
    }

    const currentPage = story.pages[currentPageIndex];

    const next = () => {
        if (currentPageIndex < story.pages.length - 1) setCurrentPageIndex(currentPageIndex + 1);
    };

    const prev = () => {
        if (currentPageIndex > 0) setCurrentPageIndex(currentPageIndex - 1);
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
            <Link to="/" className="absolute top-8 left-8 text-white/50 hover:text-white transition-colors">← Back to Library</Link>

            <div className="max-w-6xl w-full flex flex-col md:flex-row gap-12 items-center">
                {/* Image */}
                <div className="flex-1 w-full aspect-[4/3] bg-black rounded-2xl overflow-hidden shadow-2xl relative border border-white/10">
                    <AnimatePresence mode='wait'>
                        <motion.img
                            key={currentPage.image_url}
                            src={currentPage.image_url}
                            alt={`Page ${currentPage.page_number}`}
                            initial={{ opacity: 0, scale: 1.05 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.5 }}
                            className="w-full h-full object-cover"
                        />
                    </AnimatePresence>
                </div>

                {/* Text & Controls */}
                <div className="flex-1 flex flex-col gap-8 max-w-lg">
                    <motion.div
                        key={currentPage.text_content}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <h2 className="text-2xl md:text-3xl font-serif leading-relaxed text-gray-100">{currentPage.text_content}</h2>
                    </motion.div>

                    {currentPage.audio_url && currentPage.audio_url !== "" && (
                        <audio controls src={`http://localhost:8000${currentPage.audio_url}`} className="w-full opacity-80 hover:opacity-100 transition-opacity" autoPlay />
                    )}

                    {(!currentPage.audio_url || currentPage.audio_url === "") && (
                        <button
                            onClick={async () => {
                                try {
                                    await generateAudio(story.id);
                                    // Reload story to get updated audio URLs
                                    loadStory(story.id);
                                } catch (e) {
                                    console.error('Failed to generate audio', e);
                                }
                            }}
                            className="px-6 py-3 bg-green-600 text-white font-medium rounded-full hover:bg-green-500 transition"
                        >
                            🎵 Generate Audio
                        </button>
                    )}

                    <div className="flex justify-between items-center mt-4 pt-8 border-t border-white/10">
                        <button
                            onClick={prev}
                            disabled={currentPageIndex === 0}
                            className="px-6 py-3 bg-white/5 rounded-full disabled:opacity-30 hover:bg-white/10 transition font-medium"
                        >
                            Previous
                        </button>
                        <span className="text-white/40 font-mono text-sm">Page {currentPageIndex + 1} / {story.pages.length}</span>
                        <button
                            onClick={next}
                            disabled={currentPageIndex === story.pages.length - 1}
                            className="px-6 py-3 bg-indigo-500 text-white font-bold rounded-full disabled:opacity-30 hover:bg-indigo-400 transition shadow-lg shadow-indigo-500/20"
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
