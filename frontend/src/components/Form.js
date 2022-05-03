import Menu from './Menu';
import SearchBar from './SearchBar';
import DepthSlider from './DepthSlider';
import SubmitButton from './SubmitButton';
import React from 'react';

const API_URI = 'http://127.0.0.1:8000/api/'

const defaultValues = {
    modeGraph: true,
    left: "",
    right: "",
    root: "",
    depth: 0,
}

class Form extends React.Component {

    constructor(props) {
        super(props)
        this._menu   = React.createRef()
        this._left   = React.createRef()
        this._right  = React.createRef()
        this._root   = React.createRef()
        this._slider = React.createRef()
        this.state = {
            ...defaultValues,
            onSubmit: props.defaultValues
        }
    }
    
    getRef(id) {
        if (id === 'menu')   return this._menu
        if (id === 'left')   return this._left
        if (id === 'right')  return this._right
        if (id === 'root')   return this._root
        if (id === 'depth')  return this._slider
    }

    handleTextfieldChange = (event) => {
        const {name, value} = event.target;
        try {
            fetch(API_URI + 'exists?search=' + value)
                .then(response => {
                    if (response.ok) {
                        return response.json()
                    } else {
                        throw new Error ('Backend query failed')
                    }
                })
                .then(json => {
                    if (json.nodeExists) {
                        this.getRef(event.target.id).current.clearError()
                        this.setState({[name]: value})
                    } else {
                        this.getRef(event.target.id).current.error('Nincs ilyen színész / film az adatbázisban!')
                        this.setState({[name]: ''})
                    }
                })
        } catch(error) {
            console.log(error)
        }

    }

    handleSliderChange = (event) => {
        const {name, value} = event.target;
        this.setState({[name]: value})
        this.setState({
            ...this.state,
            [name]: value
        })
        console.log(value)
        console.log(this.state)
    }

    handleModeSwitch = (event) => {
        this.setState({
            modeGraph: event.target.id === 'graphButton'
        })
        this._menu.current.setMode(this.state.modeGraph)
        this.forceUpdate()
        this._menu.current.forceUpdate()
    }

    getURI() {
        if (this.state.modeGraph) {
                return(API_URI + 'graph?root=' + this.state.root + '&depth=' + this.state.depth)
        } else {
                return(API_URI + 'path?left=' + this.state.left + '&right=' + this.state.right)
        }
    }

    render() {
        return(
            <form id="settings" onSubmit={this.state.onSubmit}>
                <Menu
                    ref={this._menu}
                    modeGraph={this.state.modeGraph}
                    onClick={this.handleModeSwitch}
                />
                <SearchBar
                    ref={this._left}
                    name="left"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleTextfieldChange}
                    // hidden={this.state.modeGraph}
                />
                <SearchBar
                    ref={this._right}
                    name="right"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleTextfieldChange}    
                    // hidden={this.state.modeGraph}
                />
                <SearchBar
                    ref={this._root}
                    name="root"
                    label="Színész / film"
                    value={this.state.name}
                    onChange={this.handleTextfieldChange}    
                    // hidden={!this.state.modeGraph}
                />
                <DepthSlider
                    name='depth'
                    value={this.state.depth}
                    max={4}
                    onChange={this.handleSliderChange}
                    // hidden={!this.state.modeGraph}
                />
                <SubmitButton/>
            </form>
        )
    }
}

export default Form