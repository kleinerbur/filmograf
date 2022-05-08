import TextField from '@mui/material/TextField';
import React from 'react';
import './Form.css';

const defaultStyle = {
    minWidth: 400,
    maxWidth: 400,
    fontFamily: 'Bahnschrift',
    fontSize: '15pt',
    color: 'white',
    '& label': {
        fontFamily: 'Bahnschrift',
    },
    '& label.Mui-focused': {
        color: 'white',
        fontFamily: 'Bahnschrift',
    },
    input: {
        color: 'white'
    }
}


class SearchBar extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            name: props.name,
            label: props.label,
            value: props.value,
            onChange: props.onChange,   

            error: false,
            helperText: '',
            hidden: props.hidden
        }
    }

    error(helperText) {
        this.setState({
            error: true,
            helperText: helperText
        })
    }

    clearError() {
        this.setState({
            error: false,
            helperText: ''
        })
    }

    hide   = () => this.setState({hidden: true})
    unhide = () => this.setState({hidden: false})

    render() {
        if (this.state.hidden) return (<></>)
        return (<TextField
                    className='.fgrafSearchBar'
                    id={this.state.name}
                    name={this.state.name}
                    label={this.state.label}
                    
                    variant='filled'
                    color='secondary'
                    type="text"
                    sx={defaultStyle}
                    
                    hidden={this.state.hidden}

                    error={this.state.error}
                    helperText={this.state.helperText}
                    
                    onChange={this.state.onChange}/>)
    }
}

export default SearchBar;