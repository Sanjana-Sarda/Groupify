function Login() {
    return React.createElement(
        'div',
        { className: 'center' },
        React.createElement(LoginButton, { text: 'Log in with Spotify' })
    );
}
ReactDOM.render(React.createElement(Login, null), document.getElementById('login-mount-point'));