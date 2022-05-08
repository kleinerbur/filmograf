import './App.css';
import Form from './components/Form';
import FilmGraph from './components/FilmGraph';
import React from 'react';
import ReactDOM from 'react-dom/client';

class App extends React.Component {

    constructor(props){
		super(props)
		this._form  = React.createRef()
	}

	handleSubmit = (event) => {
		const canvas = document.getElementById('canvas')
		const canvasWidth  = canvas.clientWidth;
		const canvasHeight = canvas.clientHeight;

		const canvasRoot = ReactDOM.createRoot(canvas)
		canvasRoot.render(<FilmGraph width={canvasWidth} height={canvasHeight} uri={this._form.current.getURI()}/>)
	}

    render() {
        return (
			<header className="App-header">
				<Form ref={this._form} onSubmit={this.handleSubmit}/>
			</header>
        );
    }
}

export default App;
