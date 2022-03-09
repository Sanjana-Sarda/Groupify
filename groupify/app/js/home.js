class Home extends React.Component {
  constructor() {
    super();
    this.state = {};
  }
  componentDidMount() {
    if (getCookie("username")) {
      this.setState({ username: getCookie("username"), loggedIn: true });
    }
  }
  render() {
    if (this.state.loggedIn) {
      return (
        <div>
          <TopBar />
          <div className="welcome-box">
            <h1 style={{ marginBottom: "15px", color: "#6800EC" }}>
              Hi, {this.state.username}!
            </h1>
            <br />
            <Functions />
          </div>
        </div>
      );
    } else {
      return (
        <div>
          <TopBar left="none" />
          <div className="center">
            <h1 style={{ color: "black", fontSize: "40px", align: "center" }}>
              Welcome to Groupify!
            </h1>
            <h2
              style={{
                color: "black",
                fontSize: "20px",
                align: "center",
              }}
            >
              <em>
                Get ready to create the group playlist with songs everyone will
                love
              </em>
            </h2>
            <br />
            <LoginButton className="noselect" text="Log in with Spotify" />
          </div>
        </div>
      );
    }
  }
}

ReactDOM.render(<Home />, document.getElementById("home-mount-point"));
