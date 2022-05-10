import './App.css';
import Form from './components/Form';
import FilmGraph from './components/FilmGraph';
import React from 'react';
import ReactDOM from 'react-dom/client';

import Drawer from '@mui/material/Drawer'

import Fab from '@mui/material/Fab';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

class App extends React.Component {

    constructor(props){
		super(props)
		this._form  = React.createRef()
		this._graph = React.createRef()
		this.state = {
			openLeftDrawer: false,
			openRightDrawer: false,
			poster_src: '',
			poster_label: '',
			poster_alt: '',
			imdb_uri: ''
		}
	}

	handleSubmit = (event) => {
		this._form.current.setDistance()

		const canvas = document.getElementById('canvas')
		const canvasWidth  = canvas.clientWidth;
		const canvasHeight = canvas.clientHeight;

		const canvasRoot = ReactDOM.createRoot(canvas)
		canvasRoot.render(<FilmGraph ref={this._graph} width={canvasWidth} height={canvasHeight} uri={this._form.current.getURI()} events={{doubleClick: this.openLeftDrawer}}/>)
	}

	closeRightDrawer = () => this.setState({openRightDrawer: false})
	closeLeftDrawer  = () => this.setState({
									openLeftDrawer: false,
									poster_src: '',
									poster_label: '',
									poster_alt: '',
									imdb_uri: ''
								})


	openRightDrawer = (event) => {
		this.closeRightDrawer()
		this.setState({openRightDrawer: true})
	}
	openLeftDrawer  = (event) => {
		this.closeLeftDrawer()
        var id = this._graph.current._network.current.Network.getSelectedNodes()[0]
        var selectedNode = this._graph.current.state.nodes.filter(n => n.id === id)[0]
		console.log(selectedNode)
		this.setState({
			openLeftDrawer: true,
			poster_src: selectedNode.poster,
			poster_alt: selectedNode.label + ' teljes méretű posztere.',
			imdb_uri: selectedNode.uri
		})
		if (selectedNode.group === 'actors') {
			this.setState({
				poster_label: selectedNode.label
			})
		}
	}

	handleDrawerKeyDown = (event) => {
		if (event.code === 'Escape') {
			this.closeLeftDrawer()
			this.closeRightDrawer()
		}
	}

	handleBackdropClick = (event) => {
		this.closeLeftDrawer()
		this.closeRightDrawer()
	}

    render() {
        return (
			<div>
				<header className="App-header">
					<Form ref={this._form} onSubmit={this.handleSubmit}/>
					
					<Drawer className='info-panel'
						anchor='left'
						open={this.state.openLeftDrawer}
						onKeyDown={this.handleDrawerKeyDown}
						ModalProps={{ onBackdropClick: this.handleBackdropClick }}
						sx={{
							alignItems: 'center',
							width: 400,
							overflow: 'hidden'
						}}
					>
						<img src={this.state.poster_src}
							alt={this.state.poster_alt}
							style={{
								height: '100%',
								width: 700,
								objectFit: 'cover'
							}}/>
						<h1 className='posterlabel'>{this.state.poster_label}</h1>
						<a href={this.state.imdb_uri} target='_blank' rel="noreferrer">
							<img className='imdb-button'
								src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/575px-IMDB_Logo_2016.svg.png'
								alt="IMDb logó - kattints ide a színész/film IMDb oldalának megtekintéséhez!"
							/>
						</a>
					</Drawer>

					<Drawer className='help-panel'
						anchor='right'
						open={this.state.openRightDrawer}
						onKeyDown={this.handleDrawerKeyDown}
						ModalProps={{ onBackdropClick: this.handleBackdropClick }}
						sx={{
							alignItems: 'center',
							width: 400,
							overflow: 'hidden'
						}}
					>
						<h1>film-o-gráf</h1>
						<p>Lorem ipsum dolor sit amet</p>
					</Drawer>
				</header>
				<Fab color='primary' aria-label='?' onClick={this.openRightDrawer}
					sx={{
						position: 'absolute',
						bottom: 20,
						right: 20,
					}}>
					<QuestionMarkIcon/>
				</Fab>
			</div>
        );
    }
}

export default App;
