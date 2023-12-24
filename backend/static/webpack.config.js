const path = require('path');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const webpack = require('webpack');
const globAll = require('glob-all');


const matchedFiles = globAll.sync([
  path.join(__dirname, '**/*.{css,js,scss}'),
], {
  absolute: false,
  deep: 15,
});

console.log(matchedFiles);

module.exports = {
  entry: {
    main: matchedFiles.filter(item => item && path.extname(item) !== ''),
  },
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: '[name].[contenthash].bundle.js'
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        test: /\.js(\?.*)?$/i,
      }),
      new CssMinimizerPlugin(),
    ],
    splitChunks: {
      chunks: 'all',
    },
    runtimeChunk: 'single',
  },
  plugins: [
    new webpack.ProvidePlugin({
      Chart: 'chart.js',
    }),
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(s[ac]ss|css)$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader',
        ],
      },
    ],
  },
  devtool: process.env.NODE_ENV === 'development' ? 'source-map' : false,
};
