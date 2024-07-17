import React, { useEffect, useState } from 'react';
import axios from 'axios';

const SpotifyData = () => {
    const [userData, setUserData] = useState(null);
    const [playlistData, setPlaylistData] = useState(null);
    const [likedData, setLikedData] = useState(null);

//set user data
    useEffect(() => {
        axios.get("/api/user")
            .then(res => {
                setUserData(res.data)
            }).catch(err => {
                console.log(err)
            })
    }, []);

    useEffect(() => {
        axios.get("/api/playlists")
            .then(res=> {
                setPlaylistData(res.data)     
            }).catch(err => {
                console.log(err)
            })
    }, []);

    useEffect(() => {
        axios.get("/api/tracks")
            .then(res => {
                setLikedData(res.data)
            }).catch(err => {
                console.log(err)
            })
    }, []);
    return (
        <div>
            {userData ? (
                <>
                    <p>User: {userData.display_name}</p>
                    <h2>Playlists:</h2>
                    {playlistData && playlistData.items ? (
                        <ul>
                            {playlistData.items.map((playlist, index) => (
                                <li key={index}>{playlist.name}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>Loading playlists...</p>
                    )}
                </>
            ) : (
                <p>Loading user data...</p>
            )}
        </div>
    );
};

export default SpotifyData;
