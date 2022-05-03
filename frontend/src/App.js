// import logo from './logo.svg';
import './App.css';
import Form from './components/Form';
import FilmGraph from './components/FilmGraph';
import React from 'react';

class App extends React.Component {

    constructor(props){
		super(props)
		this._form = React.createRef()
		this.state = {
			uri: ''
		}
	}

	submit = (event) => {
		event.preventDefault();
		console.log(event)
		console.log(this._form.current.getURI())
		this.setState({
			uri: this._form.current.getURI()
		})
	}

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    {/* <img src={logo} className="App-logo" alt="logo" /> */}
                    <h1 style={{fontFamily: "Bahnschrift", fontWeight: "lighter"}}>film-o-gráf</h1>

					{/* <Form ref={this._form} onSubmit={this.submit}/> */}
					<h1>{this.state.uri}</h1>
					<FilmGraph mode='graph' root='Emma Stone' depth='2'/>
                </header>
            </div>
        );
    }
}

export default App;
