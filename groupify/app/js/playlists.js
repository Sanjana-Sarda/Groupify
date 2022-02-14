class Playlists extends React.Component {
    constructor() {
        super();
        this.state = {};
    }
    render() {
        return (
            <iframe src={`https://open.spotify.com/embed/playlist/`+getCookie('playlist_id')} width="600" height="800" align="middle" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
        )
    }
}
    

ReactDOM.render(
    <Playlists />,
    document.getElementById('display-playlist')
);