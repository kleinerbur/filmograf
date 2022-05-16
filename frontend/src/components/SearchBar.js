import TextField from '@mui/material/TextField';
import React from 'react';

class SearchBar extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            name:       props.name,
            label:      props.label,
            value:      props.value,
            onChange:   props.onChange,
            onFocusOut: props.onFocusOut,   
            hidden:     props.hidden,
            error:      false,
            helperText: ''
        }
    }

    error = (helperText) =>  this.setState({
        error:      true,
        helperText: helperText
    })

    clearError = () => this.setState({
        error:      false,
        helperText: ''
    })

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
                    type='text'
                    
                    hidden={this.state.hidden}

                    error={this.state.error}
                    helperText={this.state.helperText}
                    
                    onChange={this.state.onChange}
                    onBlur={this.state.onFocusOut}/>)
    }
}

export default SearchBar;