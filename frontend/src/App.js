// eslint-disable-next-line no-unused-vars
import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './components/Home';
import Notes from './components/Notes';
import Login from './components/Login';
import Registration from './components/Registration';

function App() {
    return (
        <Router>
            <Switch>
                <Route path="/" exact component={Home} />
                <Route path="/notes" exact component={Notes} />
                <Route path="/accounts/login/" exact component={Login} />
                <Route path="/accounts/signup/" exact component={Registration} />
            </Switch>
        </Router>
    );
}

export default App;
