import Form from './components/Form';
import FilmGraph from './components/FilmGraph';

import React from 'react';
import ReactDOM from 'react-dom/client';

import LinearProgress from '@mui/material/LinearProgress';
import Drawer from '@mui/material/Drawer'
import Fab from '@mui/material/Fab';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

import './style/App.css';

class App extends React.Component {

    constructor(props){
		super(props)
		this._form  = React.createRef()
		this._graph = React.createRef()
		this.state = {
			openLeftDrawer:     false,
			openRightDrawer:    false,
			progressbar_height: 0,
			poster_src:         '',
			poster_label:       '',
			poster_alt:         '',
			imdb_uri:           ''
		}
		this.canvas = document.getElementById('canvas-container')
		this.canvasRoot = ReactDOM.createRoot(this.canvas)
	}

	handleSubmit = (event) => {
		this._form.current.setDistance()
		this.setState({progressbar_height: 5})

		this.canvasRoot.unmount()
		this.canvasRoot = ReactDOM.createRoot(this.canvas)
		this.canvasRoot.render(
			<FilmGraph 
				ref={this._graph}
				width={this.canvas.clientWidth}
				height={this.canvas.clientHeight}
				uri={this._form.current.getURI()}
				events={{
					doubleClick: this.openLeftDrawer,
					stabilized:   () => this.setState({progressbar_height: 0})
				}}/>
		)
	}

	closeRightDrawer = () => this.setState({
		openRightDrawer: false
	})

	openRightDrawer = (event) => {
		this.closeRightDrawer()
		this.setState({openRightDrawer: true})
	}
	
	closeLeftDrawer  = () => this.setState({
		openLeftDrawer: false,
		poster_src:     '',
		poster_label:   '',
		poster_alt:     '',
		imdb_uri:       ''
	})

	openLeftDrawer  = (event) => {
		this.closeLeftDrawer()
        var id = this._graph.current._network.current.Network.getSelectedNodes()[0]
        var selectedNode = this._graph.current.state.nodes.filter(n => n.id === id)[0]
		this.setState({
			openLeftDrawer: true,
			poster_src:     selectedNode.poster,
			poster_alt:     selectedNode.label + ' teljes méretű posztere.',
			imdb_uri:       selectedNode.uri
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
					
					<LinearProgress sx={{
						height: this.state.progressbar_height, 
						width: '100%'}}/>
					
					<Drawer className='info-panel'
						anchor='left'
						open={this.state.openLeftDrawer}
						onKeyDown={this.handleDrawerKeyDown}
						ModalProps={{ onBackdropClick: this.handleBackdropClick }}
					>
						<img className='poster' 
							src={this.state.poster_src}
							alt={this.state.poster_alt}/>
						<h1 className='posterlabel'>
							{this.state.poster_label}
						</h1>
						<a href={this.state.imdb_uri} target='_blank' rel="noreferrer">
							<img className='imdb-button'
								src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/575px-IMDB_Logo_2016.svg.png'
								alt="IMDb logó - kattints ide a színész/film IMDb oldalának megtekintéséhez!"
							/>
						</a>
					</Drawer>

					<Drawer className='helpPanel'
						anchor='right'
						open={this.state.openRightDrawer}
						onKeyDown={this.handleDrawerKeyDown}
						ModalProps={{ onBackdropClick: this.handleBackdropClick }}
					>
						<h2 className='title'>film-o-gráf</h2>
						<p>
							A projektet az <a href='https://oracleofbacon.org/' target='_blank' rel='noreferrer'><b>Oracle of Bacon</b></a> ihlette,
							ahol minden színészt egy numerikus értékkel ruháztak fel, ami a távolságukat mutatja Kevin Bacontől.
							<br/>
							<br/>
							X és Y távolsága 1, ha mindketten szerepeltek legalább egy közös filmben.
							X és Y távolsága 2, ha nincs közös filmjük, de mindkettőjüknek van legalább egy közös filmje Z-vel.
							(stb.)
							<br/>
							<br/>
							A film-o-gráf webalkalmazás lehetőséget ad lekérdezni a legrövidebb utat bármely két színész / film között, ehhez kattints az <b>Út </b> 
							gombra, és adj meg egy-egy kulcsszót a színészekre / filmekre. Az út csak akkor rajzolható ki, ha mindkét kulcsszó illeszkedik
							valamely rekordra az adatbázisban. Ha nem létezik út a két rekord között, a távolságuk '-'.
							<br/>
							<br/>
							A <b>Gráf</b> gombra kattintva az egyik szövegdoboz helyén egy csúszka jelenik meg, amelyen a mélységet adhatod meg.
							Egy valid kulcsszó megadása és a mélység beállítása után a <b>MEHET</b> gombra kattintva kirajzolódik egy gráf, melyben
							minden olyan film és színész szerepel, akitől a keresett színész/film távolsága legfeljebb a mélység értéke.
							<br/>
							<br/>
							A csomópontok mozgathatók, dupla kattintásra pedig megtekinthetővé válik a teljes méretű képük. A képen megjelenő IMDb 
							gomb a színész/film IMDb oldalára irányít.
							<br/>
							<br/>
							Készítette:
							<br/>
							<b>Bur Bence</b>
							<br/>
							<i>pt46p3@inf.elte.hu</i>
						</p>
					</Drawer>
				</header>
				
				<Fab color='primary' aria-label='help' onClick={this.openRightDrawer}
					sx={{
						position: 'absolute',
						bottom: 30,
						right: 30,
					}}>
					<QuestionMarkIcon/>
				</Fab>
			</div>
        )
    }
}

export default App;
