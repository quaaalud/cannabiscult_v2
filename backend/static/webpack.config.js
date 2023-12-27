const path = require('path');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const glob = require("glob");

module.exports = {
  entry: {
    main: path.resolve(__dirname, 'js/mdb.min.js'), // Assuming init.js is the entry point for JS
    styles: path.resolve(__dirname,'src/mdb/scss/mdb.pro.scss'), 
  },
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: '[name].bundle.js', // Outputs main.bundle.js for JS
    publicPath: '/',
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin(), // Minify JS
      new CssMinimizerPlugin(), // Minify CSS
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'styles.bundle.css', // Outputs styles.bundle.css for CSS
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
      {
        test: /\.js$/,
        use: 'babel-loader',
      },
    ],
  },
  devtool: process.env.NODE_ENV === 'development' ? 'source-map' : false,
};
