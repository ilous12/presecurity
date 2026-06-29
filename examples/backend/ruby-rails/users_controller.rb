class UsersController < ApplicationController
  def index
    role = params[:role]
    # Intentional fixture: request parameter is interpolated into SQL.
    @users = User.find_by_sql("select * from users where role = '#{role}'")
    render json: @users
  end
end
