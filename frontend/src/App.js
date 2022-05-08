import './App.css';
import Form from './components/Form';
import FilmGraph from './components/FilmGraph';
import React from 'react';
import ReactDOM from 'react-dom/client';

import Drawer from '@mui/material/Drawer'

class App extends React.Component {

    constructor(props){
		super(props)
		this._form  = React.createRef()
		this._graph = React.createRef()
		this.state = {
			openDrawer: false,
			image_src: '',
			image_label: '',
			image_alt: '',
			imdb_uri: ''
		}
	}

	handleSubmit = (event) => {
		this._form.current.setDistance()

		const canvas = document.getElementById('canvas')
		const canvasWidth  = canvas.clientWidth;
		const canvasHeight = canvas.clientHeight;

		const canvasRoot = ReactDOM.createRoot(canvas)
		canvasRoot.render(<FilmGraph ref={this._graph} width={canvasWidth} height={canvasHeight} uri={this._form.current.getURI()} events={{doubleClick: this.openDrawer}}/>)
	}

	closeDrawer() {
		this.setState({
			openDrawer: false,
			image_src: '',
			image_label: '',
			image_alt: '',
			imdb_uri: ''
		})
	}

	openDrawer = (event) => {
		this.closeDrawer()
        var id = this._graph.current._network.current.Network.getSelectedNodes()[0]
        var selectedNode = this._graph.current.state.nodes.filter(n => n.id === id)[0]
		console.log(selectedNode)
		this.setState({
			openDrawer: true,
			image_src: selectedNode.poster,
			image_alt: selectedNode.label + ' teljes méretű posztere.',
			imdb_uri: selectedNode.uri
		})
		if (selectedNode.group === 'actors') {
			this.setState({
				image_label: selectedNode.label
			})
		}
	}

	handleDrawerKeyDown = (event) => {
		if (event.code === 'Escape') this.closeDrawer()
	}

	handleBackdropClick = (event) => this.closeDrawer()

    render() {
        return (
			<header className="App-header">
				<Form ref={this._form} onSubmit={this.handleSubmit}/>
				<Drawer
                    anchor='left'
                    open={this.state.openDrawer}
                    hideBackdrop={false}
                    onKeyDown={this.handleDrawerKeyDown}
					ModalProps={{ onBackdropClick: this.handleBackdropClick }}
                    sx={{
                        alignItems: 'center',
                        width: 400,
                        overflow: 'hidden',
                    }}
                >
                    <img src={this.state.image_src}
                        alt={this.state.image_alt}
                        style={{
                            height: '100%',
							width: 700,
							objectFit: 'cover'
						}}/>
					<h1 className='posterlabel'>{this.state.image_label}</h1>
                    <a href={this.state.imdb_uri} target='_blank'>
                        <img className='imdb-button'
							src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/575px-IMDB_Logo_2016.svg.png'
                            alt="IMDb logó - kattints ide a színész/film IMDb oldalának megtekintéséhez!"
                        />
                    </a>
                </Drawer>
			</header>
        );
    }
}

export default App;
