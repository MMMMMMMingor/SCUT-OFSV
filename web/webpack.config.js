const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
    // mode: "development",
    mode: "production",
    resolve: {
        alias: {}
    },
    entry: {
        index: './src/index.js',
        enroll: './src/enrollment.js',
        verify: './src/verification.js',
    },
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: '[id].[contenthash].js',
    },
    plugins: [
        new CleanWebpackPlugin(),
        new HtmlWebpackPlugin({
            filename: './index.html',
            chunks: ['index'],
            template: './public/index.html'
        }),
        new HtmlWebpackPlugin({
            filename: './enroll.html',
            chunks: ['enroll'],
            template: './public/enroll.html'
        }),
        new HtmlWebpackPlugin({
            filename: './verify.html',
            chunks: ['verify'],
            template: './public/verify.html'
        }),
        new MiniCssExtractPlugin({
            filename: '[name].[contenthash].css',
            chunkFilename: '[id].[contenthash].css',
        }),
        new CssMinimizerPlugin(),
    ],
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    { loader: 'css-loader', options: { importLoaders: 1 } },
                    "postcss-loader"
                ],
            },
        ],
    },
    devServer: {
        contentBase: [
            path.join(__dirname, 'public'),
            path.join(__dirname, 'src'),
        ],
        compress: true,
        open: true,
        port: 9000,
        // hot: true,
        watchContentBase: true,
        watchOptions: {
            ignored: /node_modules/, // 略过node_modules目录
        },
    },
};