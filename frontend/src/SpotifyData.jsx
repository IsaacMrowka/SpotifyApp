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

    const handleSearchChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearchSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.get(`http://localhost:5000/api/search?q=${query}`);
            console.log(res.data)
            setResults(res.data);//checkspotify api
        } catch (err) {
            console.error('Error fetching search results', err);
        }
    };

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
                {results > 0 ? (
                    <ul>
                        {results.map((track) => (
                            <li key={track.id}>
                                {track.name}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <div>No results Found</div>
                )}
            </div>
            <div className="content">
                <div className="left-container">
                    {/* Placeholder for future data */}
                </div>
                <div className="right-container">
                    {/* Placeholder for future data */}
                </div>
            </div>
        </div>
    );
};

export default SpotifyData;