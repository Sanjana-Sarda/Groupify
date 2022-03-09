class Playlists extends React.Component {
<<<<<<< Updated upstream
    constructor() {
        super();
        this.state = {};
    }
    render() {
        return (
            <iframe src={`https://open.spotify.com/embed/playlist/`+getCookie('playlist_id')} width="600" height="800" align="middle" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
        )
    }
=======
  constructor() {
    super();
    this.state = {};
  }
  render() {
    return (
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
        }}
      >
        <div class="playlist-display">
          <h2 style={{ fontSize: "20px", align: "center" }}>
            Enjoy your group playlist!
          </h2>
        </div>
        <br />
        <iframe
          src={
            `https://open.spotify.com/embed/playlist/` +
            getCookie("playlist_id")
          }
          width="600"
          height="400"
          align="middle"
          frameBorder="0"
          allowtransparency="true"
          allow="encrypted-media"
        />
      </div>
    );
  }
>>>>>>> Stashed changes
}
    

ReactDOM.render(
    <Playlists />,
    document.getElementById('display-playlist')
);
