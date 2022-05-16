import SwitchButtons from './SwitchButtons';
import SearchBar from './SearchBar';
import DepthSlider from './DepthSlider';
import SubmitButton from './SubmitButton';
import React from 'react';

const API_URI = 'http://localhost:8000/api/'

const defaultValues = {
    modeGraph: true,
    left: "",
    right: "",
    depth: 0,
    distance: ''
}

class Form extends React.Component {

    constructor(props) {
        super(props)
        this._switch = React.createRef()
        this._left   = React.createRef()
        this._right  = React.createRef()
        this._slider = React.createRef()
        this._submit = React.createRef()
        this.state = {
            ...defaultValues,
            onSubmit: props.onSubmit
        }
		this.controller = new AbortController();
    }
    
    getRef(id) {
        if (id === 'left')   return this._left
        if (id === 'right')  return this._right
        if (id === 'switch') return this._switch
        if (id === 'depth')  return this._slider
        if (id === 'submit') return this._submit
    }

    handleSearchBarChange = (event) => {
        this._submit.current.disable()
        var searchbar = this.getRef(event.target.name).current
        searchbar.clearError()
    }

    validateSearchBar = (event) => {
        this._submit.current.disable()
        var searchbar = this.getRef(event.target.id).current
        searchbar.setState({helperText: 'Keresés...'})

        var left  = this.state.left
        var right = this.state.right
        var {name, value} = event.target

        if (value === '') {
            this.setState({[name]: ''})
            searchbar.clearError()
        } else {
            value = value.split('?').join('\\?').split('&').join('%&')
            if (this.controller.current) {
                this.controller.abort()
                this.controller = new AbortController()
            }
            fetch(API_URI + 'exists?search=' + value, this.controller.signal)
                .then(response => response.json())
                .then(json => {
                    if (json.nodeExists) {
                        searchbar.clearError()
                        this.setState({[name]: value})
                        name === 'left'
                            ? left  = value
                            : right = value
                    } else {
                        searchbar.error('Nincs ilyen színész / film az adatbázisban!')
                        this.setState({[name]: ''})
                    }})
                .then(() => {
                    if (left !== '' && (this.state.modeGraph || (!this.state.modeGraph && right !== ''))) {
                        this._submit.current.enable()
                    } else {
                        this._submit.current.disable()
                    }
                })
                .catch((error) => {
                    searchbar.error('Az adatbázis pillanatnyilag nem elérhető.')
                    console.log(error)
                })
        }
    }

    handleSliderChange = (event) => this.setState({depth: event.target.value})

    handleModeSwitch = (event) => {
        this.setState({modeGraph: event.target.id === 'graph-button'})
        if (event.target.id === 'graph-button') {
            this.setState({
                distance: '',
                right: ''
            })
            this._switch.current.graphMode()
            this._right.current.hide()
            this._slider.current.unhide()
            if (this.state.left === '')
                this._submit.current.disable()
        } else {
            this._switch.current.pathMode()
            this._right.current.unhide()
            this._slider.current.hide()
        }
    }

    getURI() {
        if (this.state.modeGraph) 
            return(API_URI + 'graph?root=' + this.state.left + '&depth=' + this.state.depth)

        var left  = this.state.left
        var right = this.state.right
        if (right === '') right = left
        if (left  === '') left  = right
        return(API_URI + 'path?left=' + left + '&right=' + right)
    }

    setDistance() {
        if (!this.state.modeGraph) {
            var left  = this.state.left
            var right = this.state.right
            if (right === '') right = left
            if (left  === '') left  = right

            fetch(API_URI + 'distance?left=' + left + '&right=' + right)
                .then(response => response.json())
                .then(response => this.setState({distance: 'Távolság: ' + response.distance}))
                .catch((error) => this.setState({distance: 'Távolság: ?'}))
        } else {
            this.setState({distance: ''})
        }
    }

    render() {
        return(
            <ul className="form">
                <h1 className="title">film-o-gráf</h1>
                <SwitchButtons
                    ref={this._switch}
                    name='switch'
                    modeGraph={this.state.modeGraph}
                    onClick={this.handleModeSwitch}
                />
                <SearchBar
                    ref={this._left}
                    name="left"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleSearchBarChange}
                    onFocusOut={this.validateSearchBar}
                />
                <SearchBar
                    ref={this._right}
                    name="right"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleSearchBarChange}
                    onFocusOut={this.validateSearchBar}    
                    hidden={this.state.modeGraph}
                />
                <DepthSlider
                    ref={this._slider}
                    name='depth'
                    value={this.state.depth}
                    max={2}
                    onChange={this.handleSliderChange}
                    hidden={!this.state.modeGraph}
                />
                <SubmitButton
                    name='submit'
                    ref={this._submit}
                    onClick={this.state.onSubmit}
                    disabled={this.state.left === ''}
                />
                <h2 className='distanceLabel'>{this.state.distance}</h2>
            </ul>
        )
    }
}

export default Form