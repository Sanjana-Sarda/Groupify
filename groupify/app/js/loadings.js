class Loadings extends React.Component {
  constructor() {
    super();
    this.state = {};
  }
  componentDidMount() {
    this.server = io();
    this.server.on('connect', () => console.log('connected'))
    this.server.on('update', () => {
      console.log('updating')
      location.reload();
  });
  }
  render(){
    return <div><p>YO</p></div>
  }
}

ReactDOM.render(<Loadings />, document.getElementById("display-loading"));