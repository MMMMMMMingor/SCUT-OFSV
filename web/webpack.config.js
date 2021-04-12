const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
    // mode: "development",
    mode: "production",
    resolve: {
        alias: {}
    },
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: 'osv.js',
    },
    plugins: [
        new HtmlWebpackPlugin({
            filename: './osv.html',
            template: './public/index.html'
        })
    ],
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ["style-loader", "css-loader"],
            },
        ],
    }
};