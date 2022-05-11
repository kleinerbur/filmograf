import './Form.css';
import Menu from './Menu';
import SearchBar from './SearchBar';
import DepthSlider from './DepthSlider';
import SubmitButton from './SubmitButton';
import React from 'react';

const API_URI = 'http://localhost:8000/api/'

const defaultValues = {
    modeGraph: true,
    left: "",
    right: "",
    root: "",
    depth: 0,
    distance: ''
}

class Form extends React.Component {

    constructor(props) {
        super(props)
        this._menu   = React.createRef()
        this._left   = React.createRef()
        this._right  = React.createRef()
        this._slider = React.createRef()
        this._submit = React.createRef()
        this.state = {
            ...defaultValues,
            onSubmit: props.onSubmit
        }
    }
    
    getRef(id) {
        if (id === 'menu')   return this._menu
        if (id === 'left')   return this._left
        if (id === 'right')  return this._right
        if (id === 'depth')  return this._slider
    }

    handleSearchBarChange = (event) => {
        this._submit.current.disable()
        const {name, value} = event.target;
        if (value === '') {
            this.setState({[name]: ''})
            this._submit.current.disable()
            return
        }
        var searchbar = this.getRef(event.target.id).current
        fetch(API_URI + 'exists?search=' + value)
            .then(response => response.json())
            .then(json => {
                if (json.nodeExists) {
                    searchbar.clearError()
                    this.setState({[name]: value})
                    this._submit.current.enable()
                } else {
                    searchbar.error('Nincs ilyen színész / film az adatbázisban!')
                    this.setState({[name]: ''})
                    this._submit.current.disable()
                }})
            .catch((error) => searchbar.error('Az adatbázis pillanatnyilag nem elérhető.'))
    }

    handleSliderChange = (event) => this.setState({depth: event.target.value})

    handleModeSwitch = (event) => {
        this.setState({modeGraph: event.target.id === 'graphButton'})
        if (event.target.id === 'graphButton') {
            this._menu.current.graphMode()
            this._right.current.hide()
            this._slider.current.unhide()
        } else {
            this._menu.current.pathMode()
            this._right.current.unhide()
            this._slider.current.hide()
        }
    }

    getURI() {
        if (this.state.modeGraph)
            return(API_URI + 'graph?root=' + this.state.left + '&depth=' + this.state.depth)
        return(API_URI + 'path?left=' + this.state.left + '&right=' + this.state.right)
    }

    setDistance() {
        if (!this.state.modeGraph) {
                fetch(API_URI + 'distance?left=' + this.state.left + '&right=' + this.state.right)
                    .then(response => response.json())
                    .then(response => this.setState({distance: 'Távolság: ' + response.distance}))
                    .catch((error) => this.setState({distance: 'Távolság: ?'}))
        } else {
            this.setState({distance: ''})
        }
    }

    render() {
        return(
            <ul id='form' className="searchMenu">
                <h2 style={{fontFamily: "Bahnschrift", fontWeight: "lighter", marginRight: 100, marginLeft: 50}}>film-o-gráf</h2>
                <Menu className="modeButtons"
                    ref={this._menu}
                    modeGraph={this.state.modeGraph}
                    onClick={this.handleModeSwitch}
                />
                <SearchBar
                    ref={this._left}
                    name="left"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleSearchBarChange}
                />
                <SearchBar
                    ref={this._right}
                    name="right"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleSearchBarChange}    
                    hidden={this.state.modeGraph}
                />
                <DepthSlider
                    ref={this._slider}
                    name='depth'
                    value={this.state.depth}
                    max={4}
                    onChange={this.handleSliderChange}
                    hidden={!this.state.modeGraph}
                />
                <SubmitButton
                    ref={this._submit}
                    onClick={this.state.onSubmit}
                    disabled={this.state.left === ''}
                />
                <h3 style={{fontFamily: "Bahnschrift", fontWeight: "lighter", margin: 'auto', marginLeft: 200}}>{this.state.distance}</h3>
            </ul>
        )
    }
}

export default Form