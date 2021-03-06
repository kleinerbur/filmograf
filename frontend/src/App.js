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
			openInfoDrawer:     false,
			openHelpDrawer:     false,
			progressbar_height: 0,
			poster_src:         '',
			poster_label:       '',
			poster_alt:         '',
			imdb_uri:           '',
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
					doubleClick: this.openInfoDrawer,
					stabilized:   () => this.setState({progressbar_height: 0})
				}}/>
		)

		setTimeout(() => this.setState({progressbar_height: 0}), 30000)
	}

	closeHelpDrawer = () => this.setState({
		openHelpDrawer: false
	})

	openHelpDrawer = (event) => {
		this.closeHelpDrawer()
		this.setState({openHelpDrawer: true})
	}
	
	closeInfoDrawer  = () => this.setState({
		openInfoDrawer: false,
		poster_src:     '',
		poster_label:   '',
		poster_alt:     '',
		imdb_uri:       ''
	})

	openInfoDrawer  = (event) => {
		this.closeInfoDrawer()
		try {
			var id = this._graph.current._network.current.Network.getSelectedNodes()[0]
			var selectedNode = this._graph.current.state.nodes.filter(n => n.id === id)[0]
			this.setState({
				openInfoDrawer: true,
				poster_src:     selectedNode.poster,
				poster_alt:     selectedNode.label + ' teljes m??ret?? posztere.',
				imdb_uri:       selectedNode.uri
			})
			if (selectedNode.group === 'actors') {
				this.setState({
					poster_label: selectedNode.label
				})
			}
		} catch (error) {
			// no node was selected
		}
	}

	handleDrawerKeyDown = (event) => {
		if (event.code === 'Escape') {
			this.closeInfoDrawer()
			this.closeHelpDrawer()
		}
	}

	handleBackdropClick = (event) => {
		this.closeInfoDrawer()
		this.closeHelpDrawer()
	}

    render() {
        return (
			<div>
				<header className="App-header">
					<Form ref={this._form} onSubmit={this.handleSubmit}/>					
					
					<LinearProgress color='secondary' sx={{
						height: this.state.progressbar_height, 
						width: '100%'}}/>
					
					<Drawer className='info-panel'
						anchor='right'
						open={this.state.openInfoDrawer}
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
								alt="IMDb log?? - kattints ide a sz??n??sz/film IMDb oldal??nak megtekint??s??hez!"
							/>
						</a>
					</Drawer>

					<Drawer className='help-panel'
						anchor='left'
						open={this.state.openHelpDrawer}
						onKeyDown={this.handleDrawerKeyDown}
						ModalProps={{ onBackdropClick: this.handleBackdropClick }}
					>
						<h2 className='title'>film-o-gr??f</h2>
						<p>
							A projektet az <a href='https://oracleofbacon.org/' target='_blank' rel='noreferrer'><b>Oracle of Bacon</b></a> ihlette,
							ahol minden sz??n??szt egy numerikus ??rt??kkel ruh??ztak fel, ami a t??vols??gukat mutatja Kevin Bacont??l.
							<br/>
							<br/>
							X ??s Y t??vols??ga 1, ha mindketten szerepeltek legal??bb egy k??z??s filmben.
							X ??s Y t??vols??ga 2, ha nincs k??z??s filmj??k, de mindkett??j??knek van legal??bb egy k??z??s filmje Z-vel.
							(stb.)
							<br/>
							<br/>
							A film-o-gr??f webalkalmaz??s lehet??s??get ad lek??rdezni a legr??videbb utat b??rmely k??t sz??n??sz / film k??z??tt, ehhez kattints az <b>??t </b> 
							gombra, ??s adj meg egy-egy kulcssz??t a sz??n??szekre / filmekre. Az ??t csak akkor rajzolhat?? ki, ha mindk??t kulcssz?? illeszkedik
							valamely rekordra az adatb??zisban. Ha nem l??tezik ??t a k??t rekord k??z??tt, a t??vols??guk '-'.
							<br/>
							<br/>
							A <b>Gr??f</b> gombra kattintva az egyik sz??vegdoboz hely??n egy cs??szka jelenik meg, amelyen a m??lys??get adhatod meg.
							Egy valid kulcssz?? megad??sa ??s a m??lys??g be??ll??t??sa ut??n a <b>MEHET</b> gombra kattintva kirajzol??dik egy gr??f, melyben
							minden olyan film ??s sz??n??sz szerepel, akit??l a keresett sz??n??sz/film t??vols??ga legfeljebb a m??lys??g ??rt??ke.
							<br/>
							<br/>
							A csom??pontok mozgathat??k, dupla kattint??sra pedig megtekinthet??v?? v??lik a teljes m??ret?? k??p??k. A k??pen megjelen?? IMDb 
							gomb a sz??n??sz/film IMDb oldal??ra ir??ny??t. A gr??f ??lein a sz??n??sz filmben j??tszott szerepe olvashat??.
							<br/>
							<br/>
							<br/>
							<br/>
							K??sz??tette:
							<br/>
							<b>Bur Bence</b>
							<br/>
							<i>pt46p3@inf.elte.hu</i>
						</p>
					</Drawer>
				</header>
				
				<Fab id='help'
					aria-label='help'
					color='secondary'
					onClick={this.openHelpDrawer}
					sx={{
						position: 'absolute',
						bottom: 20,
						left: 20
					}}>
					<QuestionMarkIcon/>
				</Fab>
			</div>
        )
    }
}

export default App;
