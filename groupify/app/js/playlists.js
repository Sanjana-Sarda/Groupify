class Playlists extends React.Component {
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
        <p>YO</p>
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
}

ReactDOM.render(<Playlists />, document.getElementById("display-playlist"));
