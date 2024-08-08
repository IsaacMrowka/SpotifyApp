import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SpotifyData = ({ userData }) => {
    const [playlistData, setPlaylistData] = useState(null);
    const [likedData, setLikedData] = useState(null);
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    useEffect(() => {
        if (userData) {
            fetchData('/api/playlists', setPlaylistData);
            fetchData('/api/tracks', setLikedData);
            fetchData('/api/search', setResults)
        }
    }, [userData]);

    const fetchData = async (url, setData) => {
        try {
            const res = await axios.get(url, { withCredentials: true });
            setData(res.data);
        } catch (err) {
            console.error(err);
        }
    };
    const sendData = async (url, data) => {
        try {
            const res = await axios.post(url, data, { withCredentials: true });
            console.log('Data sent successfully:', res.data);
            // Handle response if needed
        } catch (err) {
            console.error('Error sending data:', err);
        }
    };

    const handleSaveQuery = async (query) => {
        try {
            await sendData('/api/search', { query });
        } catch (err) {
            console.error('Error sending query:', err);
        }
    };

    const handleSearchChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearchSubmit = async (e) => {
        e.preventDefault();
        try {
            await handleSaveQuery(query);  // Use handleSaveQuery to send data
        } catch (err) {
            console.error('Error sending query:', err);
        }
    };
    
    //get queried id and place it {result} into spotify embeds
    //get playlsit id and place it into embeds
    return (
        <div className="spotify-data">
            <form className="search-bar" onSubmit={handleSearchSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={handleSearchChange}
                    placeholder="Search for track"
                />
                <button type="submit">Search</button>
            </form>
            <div>
                {results && (
                    <div>
                        <iframe src="https://open.spotify.com/embed/track/3vT8gzLffHjauZNwt4BtPN?utm_source=generator" width="100%" height="100" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    </div>           
                )}
            </div>
            <div className="content">
                <div className="left-container">
                    <iframe src="https://open.spotify.com/embed/playlist/0vXnd42buRJJJJSWMb2NQf?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    {/* Placeholder for future data */}
                </div>
                <div className="right-container">
                    <iframe src="https://open.spotify.com/embed/playlist/0vXnd42buRJJJJSWMb2NQf?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    {/* Placeholder for future data */}
                </div>
            </div>
        </div>
    );
};

export default SpotifyData;